<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Mi malla académica';
		// let eInscripcion = {};
		// let eCarrera = {};
		let eMalla = {};
		let ePersona = {};
		// let ePeriodoAcademia = {};
		// let eMatricula = {};
		// let eNivelMalla = {};
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			const [res, errors] = await apiGET(fetch, 'alumno/horario', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						return {
							status: 302,
							redirect: '/'
						};
					}
				} else {
					//console.log(res.data);
					Title = res.data.Title;
					// eInscripcion = res.data.eInscripcion;
					// eCarrera = eInscripcion.carrera;
					eMalla = res.data.eMalla;
					ePersona = res.data.eInscripcion.persona;
					// eMatricula = res.data.eMatricula;
					// ePeriodoAcademia = res.data.ePeriodoAcademia;
					// eNivelMalla = res.data.eNivelMalla;
				}
			}
		} else {
			return {
				status: 302,
				redirect: '/login'
			};
		}
		return {
			props: {
				Title,
				// eInscripcion,
				// ePeriodoAcademia,
				ePersona,
				// eMatricula,
				// eCarrera,
				eMalla
				// eNivelMalla
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount, onDestroy } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { Icon, Spinner } from 'sveltestrap';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponenteConsultaClase from './_componenteConsultaClase.svelte';
	import ComponentAula from './_componenteAula.svelte';

	const DEBUG = import.meta.env.DEV;
	export let Title = 'Mi horario de clases';
	// export let eInscripcion;
	export let ePersona;
	// export let eMatricula;
	// export let ePeriodoAcademia;
	export let eMalla;
	// export let eCarrera;
	// export let eNivelMalla;
	let itemsBreadCrumb = [{ text: 'Mi horario de clases', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let isClasesActuales = false;
	let isClasesPasadas = false;
	let can_reload_schedules = true;
	let can_reload_class = false;
	let load = false;
	let aSemana = [];
	let aTurnos = [];
	let aTipoHorarioClasesActuales = [];
	let aTipoHorarioClasesPasadas = [];
	let eClase = {};
	let token_clase = '';
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	let modalSize = 'md';
	let interval_1;
	let clientNavegador;
	let clientOS;
	let clientScreensize;
	let contadoPeticiones = 0;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		clienteInfo(window);
		await loadInitial(true);
		interval_1 = setInterval(function () {
			//console.log("sigue interval_1");
			loadIntervalInit();
		}, 300000);
	});

	onDestroy(() => {
		if (interval_1) {
			//console.log("destruye interval_1")
			clearInterval(interval_1);
		}
	});
	const clienteInfo = async (window) => {
		var unknown = '-';

		// browser
		const nVer = navigator.appVersion;
		const nAgt = navigator.userAgent;
		let browser = navigator.appName;
		let version = '' + parseFloat(navigator.appVersion);
		let majorVersion = parseInt(navigator.appVersion, 10);
		let nameOffset, verOffset, ix;

		// screen
		let screenSize = '';
		if (screen.width) {
			const width = screen.width ? screen.width : '';
			const height = screen.height ? screen.height : '';
			screenSize += '' + width + ' x ' + height;
		}

		// Opera
		if ((verOffset = nAgt.indexOf('Opera')) != -1) {
			browser = 'Opera';
			version = nAgt.substring(verOffset + 6);
			if ((verOffset = nAgt.indexOf('Version')) != -1) {
				version = nAgt.substring(verOffset + 8);
			}
		}
		// Opera Next
		if ((verOffset = nAgt.indexOf('OPR')) != -1) {
			browser = 'Opera';
			version = nAgt.substring(verOffset + 4);
		}
		// MSIE
		else if ((verOffset = nAgt.indexOf('MSIE')) != -1) {
			browser = 'Microsoft Internet Explorer';
			version = nAgt.substring(verOffset + 5);
		}
		// EDGE
		else if (nAgt.indexOf('Edg/') != -1) {
			browser = 'Microsoft Edge';
			version = nAgt.substring(nAgt.indexOf('Edg/') + 4);
		}
		// Chrome
		else if ((verOffset = nAgt.indexOf('Chrome')) != -1) {
			browser = 'Chrome';
			version = nAgt.substring(verOffset + 7);
		}
		// Safari
		else if ((verOffset = nAgt.indexOf('Safari')) != -1) {
			browser = 'Safari';
			version = nAgt.substring(verOffset + 7);
			if ((verOffset = nAgt.indexOf('Version')) != -1) {
				version = nAgt.substring(verOffset + 8);
			}
		}
		// Firefox
		else if ((verOffset = nAgt.indexOf('Firefox')) != -1) {
			browser = 'Firefox';
			version = nAgt.substring(verOffset + 8);
		}
		// MSIE 11+
		else if (nAgt.indexOf('Trident/') != -1) {
			browser = 'Microsoft Internet Explorer';
			version = nAgt.substring(nAgt.indexOf('rv:') + 3);
		}
		// Other browsers
		else if ((nameOffset = nAgt.lastIndexOf(' ') + 1) < (verOffset = nAgt.lastIndexOf('/'))) {
			browser = nAgt.substring(nameOffset, verOffset);
			version = nAgt.substring(verOffset + 1);
			if (browser.toLowerCase() == browser.toUpperCase()) {
				browser = navigator.appName;
			}
		}
		// trim the version string
		if ((ix = version.indexOf(';')) != -1) version = version.substring(0, ix);
		if ((ix = version.indexOf(' ')) != -1) version = version.substring(0, ix);
		if ((ix = version.indexOf(')')) != -1) version = version.substring(0, ix);

		majorVersion = parseInt('' + version, 10);
		if (isNaN(majorVersion)) {
			version = '' + parseFloat(navigator.appVersion);
			majorVersion = parseInt(navigator.appVersion, 10);
		}

		// mobile version
		const mobile = /Mobile|mini|Fennec|Android|iP(ad|od|hone)/.test(nVer);

		// system
		let os = unknown;
		let clientStrings = [
			{ s: 'Windows 10', r: /(Windows 10.0|Windows NT 10.0)/ },
			{ s: 'Windows 8.1', r: /(Windows 8.1|Windows NT 6.3)/ },
			{ s: 'Windows 8', r: /(Windows 8|Windows NT 6.2)/ },
			{ s: 'Windows 7', r: /(Windows 7|Windows NT 6.1)/ },
			{ s: 'Windows Vista', r: /Windows NT 6.0/ },
			{ s: 'Windows Server 2003', r: /Windows NT 5.2/ },
			{ s: 'Windows XP', r: /(Windows NT 5.1|Windows XP)/ },
			{ s: 'Windows 2000', r: /(Windows NT 5.0|Windows 2000)/ },
			{ s: 'Windows ME', r: /(Win 9x 4.90|Windows ME)/ },
			{ s: 'Windows 98', r: /(Windows 98|Win98)/ },
			{ s: 'Windows 95', r: /(Windows 95|Win95|Windows_95)/ },
			{ s: 'Windows NT 4.0', r: /(Windows NT 4.0|WinNT4.0|WinNT|Windows NT)/ },
			{ s: 'Windows CE', r: /Windows CE/ },
			{ s: 'Windows 3.11', r: /Win16/ },
			{ s: 'Android', r: /Android/ },
			{ s: 'Open BSD', r: /OpenBSD/ },
			{ s: 'Sun OS', r: /SunOS/ },
			{ s: 'Linux', r: /(Linux|X11)/ },
			{ s: 'iOS', r: /(iPhone|iPad|iPod)/ },
			{ s: 'Mac OS X', r: /Mac OS X/ },
			{ s: 'Mac OS', r: /(MacPPC|MacIntel|Mac_PowerPC|Macintosh)/ },
			{ s: 'QNX', r: /QNX/ },
			{ s: 'UNIX', r: /UNIX/ },
			{ s: 'BeOS', r: /BeOS/ },
			{ s: 'OS/2', r: /OS\/2/ },
			{
				s: 'Search Bot',
				r: /(nuhk|Googlebot|Yammybot|Openbot|Slurp|MSNBot|Ask Jeeves\/Teoma|ia_archiver)/
			}
		];
		for (var id in clientStrings) {
			var cs = clientStrings[id];
			if (cs.r.test(nAgt)) {
				os = cs.s;
				break;
			}
		}

		let osVersion = unknown;

		if (/Windows/.test(os)) {
			osVersion = /Windows (.*)/.exec(os)[1];
			os = 'Windows';
		}

		switch (os) {
			case 'Mac OS X':
				osVersion = /Mac OS X (10[\.\_\d]+)/.exec(nAgt)[1];
				break;

			case 'Android':
				osVersion = /Android ([\.\_\d]+)/.exec(nAgt)[1];
				break;

			case 'iOS':
				osVersion = /OS (\d+)_(\d+)_?(\d+)?/.exec(nVer);
				osVersion = osVersion[1] + '.' + osVersion[2] + '.' + (osVersion[3] | 0);
				break;
		}
		window.jscd = {
			screen: screenSize,
			browser: browser,
			browserVersion: version,
			browserMajorVersion: majorVersion,
			mobile: mobile,
			os: os,
			osVersion: osVersion
		};
		//console.log(window.jscd);
		clientNavegador = window.jscd.browser + ' ' + window.jscd.browserMajorVersion;
		clientOS = window.jscd.os + ' ' + window.jscd.osVersion;
		clientScreensize = window.jscd.screen;
	};
	const loadInitial = async (initial = false) => {
		contadoPeticiones += 1;
		if (initial) {
			loading.setLoading(true, 'Cargando, espere por favor...');
		} else {
			load = true;
		}
		can_reload_schedules = false;
		if (contadoPeticiones >= 4) {
			addToast({
				type: 'warning',
				header: 'Advertencia',
				body: `Hola ${ePersona.nombre_completo}, hemos detectado que no estas activa/o`
			});
			goto('/');
		}

		const [res, errors] = await apiPOST(fetch, 'alumno/horario?time=' + new Date().getTime(), {
			action: 'loadInit'
		});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (initial) {
					loading.setLoading(false, 'Cargando, espere por favor...');
				} else {
					load = false;
				}
				can_reload_schedules = true;
				if (!res.module_access) {
					goto('/');
				}
			} else {
				aSemana = res.data.aSemana;
				aTurnos = res.data.aTurnos;
				isClasesActuales = res.data.isClasesActuales;
				isClasesPasadas = res.data.isClasesPasadas;
				aTipoHorarioClasesActuales = res.data.aTipoHorarioClasesActuales;
				aTipoHorarioClasesPasadas = res.data.aTipoHorarioClasesPasadas;
				if (initial) {
					loading.setLoading(false, 'Cargando, espere por favor...');
				} else {
					load = false;
				}
				can_reload_schedules = true;
			}
		}
		//loading.setLoading(false, 'Cargando, espere por favor...');
	};
	const loadIntervalInit = () => {
		//console.log("can_reload_schedules: ", can_reload_schedules)
		if (can_reload_schedules) {
			loadInitial(false);
		}
	};

	const actionEvent = (aClase) => {
		console.log(aClase);
		if (aClase.action_button.action == 'go_class') {
			if (aClase.action_button.wait) {
				goClass(aClase);
			} else {
				window.open(aClase.action_button.url, '_blank');
				// window.open(clase.action_button.url, '_blank', 'width=550, height=450');
			}
		} else if (aClase.action_button.action == 'go_class_asincronica') {
			goClassAsincronica(aClase);
		}
	};

	const goClass = (aClase) => {
		eClase = aClase;
		can_reload_schedules = false;
		can_reload_class = true;
		token_clase = aClase.action_button.key;
		aDataModal = { eClase: eClase, can_reload_class: can_reload_class };
		modalDetalleContent = ComponenteConsultaClase;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = `${aClase.tipohorario_display}`;
		modalSize = 'xs';
	};

	const goClassAsincronica = async (aClase) => {
		eClase = aClase;
		can_reload_schedules = false;
		can_reload_class = false;
		loading.setLoading(true, 'Verificando, espere por favor...');
		if (aClase.action_button.wait) {
			if (aClase.action_button.url) {
				const [res, errors] = await apiPOST(fetch, 'alumno/horario', {
					action: 'enterClassAsincroncaEstudiante',
					idc: eClase.id,
					navegador: clientNavegador,
					os: clientOS,
					screensize: clientScreensize,
					key: eClase.action_button.key
				});
				if (errors.length > 0) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
					loading.setLoading(false, 'Verificando, espere por favor...');
					goto('/');
				} else {
					if (!res.isSuccess) {
						//addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						if (!res.module_access) {
							return goto('/');
						}
						loading.setLoading(false, 'Verificando, espere por favor...');
						const msj = {
							title: `NOTIFICACIÓN`,
							html: res.message,
							type: 'warning',
							icon: 'warning',
							showCancelButton: false,
							allowOutsideClick: false,
							confirmButtonColor: '#3085d6',
							cancelButtonColor: '#d33',
							confirmButtonText: 'Aceptar',
							cancelButtonText: 'Cancelar'
						};
						Swal.fire(msj)
							.then((result) => {
								if (result.value) {
									can_reload_schedules = true;
								}
							})
							.catch((error) => {
								addToast({ type: 'error', header: 'Ocurrio un error', body: error.message });
								can_reload_schedules = true;
							});
					} else {
						//console.log(res.data);
						var a = document.createElement('a');
						a.target = '_blank';
						a.href = eClase.action_button.url;
						a.click();
						can_reload_schedules = true;
						loading.setLoading(false, 'Verificando, espere por favor...');
					}
				}
			} else {
				addToast({
					type: 'warning',
					header: `${aClase.asignatura}`,
					body: `Clase no disponible, vuelve a intentarlo más tarde`
				});
				can_reload_schedules = true;
				loading.setLoading(false, 'Verificando, espere por favor...');
			}
		} else {
			window.open(aClase.action_button.url, '_blank');
			loading.setLoading(false, 'Verificando, espere por favor...');
			can_reload_schedules = true;
		}
	};

	const closeModal = () => {
		mOpenModalGenerico = false;
		can_reload_schedules = true;
		can_reload_class = false;
	};

	const actionRun = (event) => {
		console.log(event.detail);
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModal') {
			closeModal();
		}
	};

	const openUbicacionAula = (aClase) => {
		eClase = aClase;
		can_reload_schedules = false;
		can_reload_class = false;
		aDataModal = { clase_id: eClase.id };
		modalDetalleContent = ComponentAula;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = `${aClase.asignatura} - ${aClase.aula}`;
		modalSize = 'xl';
	};

	$: {
		if (mOpenModalGenerico) {
			can_reload_schedules = false;
		} else {
			can_reload_schedules = true;
		}
	}
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>
<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
<div class="py-1 py-lg-1">
	<div class="container">
		<div class="row mb-1 justify-content-center">
			<div class="col-lg-8 col-md-12 col-12 text-center">
				<!-- caption -->
				<span class="text-info mb-3 d-block text-uppercase fw-semi-bold ls-xl"
					>{ePersona.nombre_completo}</span
				>
				<h2 class="mb-2 display-4 fw-bold ">{eMalla.carrera.nombre}</h2>
				{#if eMalla.modalidad}
					<p class="lead">MODALIDAD {eMalla.modalidad.nombre} ({eMalla.fecha_display})</p>
					´
				{/if}
			</div>
		</div>
	</div>
</div>
{#if !load}
	{#if isClasesActuales || isClasesPasadas}
		<ul class="nav nav-tabs mt-4" id="myTab" role="tablist">
			{#if isClasesActuales}
				<li class="nav-item" role="presentation">
					<button
						class="nav-link active"
						id="home-tab"
						data-bs-toggle="tab"
						data-bs-target="#home"
						type="button"
						role="tab"
						aria-controls="home"
						aria-selected="true">Clases Activas</button
					>
				</li>
			{/if}
			{#if isClasesPasadas}
				<li class="nav-item" role="presentation">
					<button
						class="nav-link"
						id="profile-tab"
						data-bs-toggle="tab"
						data-bs-target="#profile"
						type="button"
						role="tab"
						aria-controls="profile"
						aria-selected="false">Clases Culminadas</button
					>
				</li>
			{/if}
		</ul>

		<div class="tab-content" id="myTabContent">
			<div class="tab-pane fade show active" id="home" role="tabpanel" aria-labelledby="home-tab">
				{#if isClasesActuales}
					<div class="row">
						<div class="col-6">
							<div
								class="alert alert-primary mt-4"
								style="background-color: #E0E2D2 !important;"
								role="alert"
							>
								MATERIAS ACTIVAS DEL PERÍODO
							</div>
						</div>
						<div class="col-6">
							<div class="mt-4 d-flex justify-content-center">
								<!-- list -->
								<ul class="list-inline mb-0">
									{#each aTipoHorarioClasesActuales as aTipoHorario}
										<li class="list-inline-item mx-3">
											<h5 class="mb-0 d-flex align-items-center fs-5 lh-1">
												<Icon
													name="square-fill"
													class="fs-5 me-2"
													style="color: {aTipoHorario[2]} !important;"
												/>
												{aTipoHorario[1]}
											</h5>
										</li>
									{/each}
								</ul>
							</div>
						</div>
					</div>
					<div class="row mt-2">
						<div class="col-12">
							<div class="table-responsive">
								<table class="table table-bordered align-middle table-sm">
									<thead class="">
										<tr class="">
											<th scope="col" class="table-secondary text-center fs-6 p-2" />
											{#each aSemana as semana}
												<th
													scope="col"
													class="{semana.activo
														? 'table-warning'
														: 'table-secondary'} text-center fs-6 align-middle p-2">{semana.dia}</th
												>
											{/each}
										</tr>
									</thead>
									<tbody>
										{#each aTurnos as aTurno}
											<tr>
												<th
													scope="row"
													class="{aTurno.activo
														? 'table-info'
														: 'table-secondary'} text-center fs-6 align-middle p-1"
													style="max-width: 4rem; min-width: 2rem;"
												>
													{aTurno.comienza} <br />{aTurno.termina}
												</th>
												{#each aTurno.aSemanaTurnoActuales as aSemana}
													<td
														class="text-center fs-6 align-middle p-1"
														style="max-width: 10rem; min-width: 10rem;"
													>
														{#each aSemana.aClases as aClase}
															<div
																class="card mb-3 p-3"
																style="max-width: 18rem; {aClase.style_card}"
															>
																<h5 class="card-title fs-5 fw-bold ">
																	{aClase.asignatura}
																</h5>
																<h6 class="card-title fs-6 fw-bold ">
																	{aClase.nivelmalla} - {aClase.paralelo}
																</h6>
																<p class="card-text p-0 m-0">
																	<span
																		>Aula:
																		{#if aClase.tipohorario === 1}
																			<button
																				type="button"
																				class="btn btn-mini btn-link p-0 m-0"
																				on:click|preventDefault={() => openUbicacionAula(aClase)}
																				><Icon name="geo-alt-fill" /> {aClase.aula}</button
																			>
																		{:else}
																			<Icon name="geo-alt-fill" /> {aClase.aula}
																		{/if}
																	</span>
																</p>
																<p class="card-text p-0 m-0"><span>Sede: {aClase.sede}</span></p>
																<div class="card-text mt-1 badge bg-secondary text-wrap">
																	{aClase.inicio} al {aClase.fin}
																</div>
																<p class="card-text p-0 m-0">
																	<span class="badge bg-info">{aClase.tipoprofesor}</span>
																</p>
																{#if aClase.profesor}
																	<div class="card-text mt-1 badge bg-secondary text-wrap">
																		{aClase.profesor}
																	</div>
																{/if}
																{#if aClase.grupoprofesor}
																	<p class="card-text p-0 m-0">
																		<span class="badge bg-info">{aClase.grupoprofesor}</span>
																	</p>
																{/if}
																{#if aClase.tipohorario_display}
																	<p class="card-text p-0 m-0">{aClase.tipohorario_display}</p>
																{/if}

																{#if aClase.action_button.action}
																	<button
																		type="button"
																		class="btn btn-sm {aClase.action_button.style_class}"
																		on:click|preventDefault={() => actionEvent(aClase)}
																		><Icon name={aClase.action_button.icon} />
																		{aClase.action_button.verbose}</button
																	>
																{/if}
															</div>
														{/each}
													</td>
												{/each}
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>
					</div>
				{/if}
			</div>
			<div class="tab-pane fade" id="profile" role="tabpanel" aria-labelledby="profile-tab">
				{#if isClasesPasadas}
					<div class="row">
						<div class="col-6">
							<div
								class="alert alert-primary mt-4"
								style="background-color: #E0E2D2 !important;"
								role="alert"
							>
								MATERIAS CULMINADAS DEL PERÍODO
							</div>
						</div>
					</div>
					<div class="row mt-2">
						<div class="col-12">
							<div class="table-responsive">
								<table class="table table-bordered align-middle table-sm">
									<thead class="">
										<tr class="">
											<th scope="col" class="table-secondary text-center fs-6 p-2" />
											{#each aSemana as semana}
												<th
													scope="col"
													class="{semana.activo
														? 'table-warning'
														: 'table-secondary'} text-center fs-6 align-middle p-2">{semana.dia}</th
												>
											{/each}
										</tr>
									</thead>
									<tbody>
										{#each aTurnos as aTurno}
											<tr>
												<th
													scope="row"
													class="{aTurno.activo
														? 'table-info'
														: 'table-secondary'} text-center fs-6 align-middle p-1"
													style="max-width: 4rem; min-width: 2rem;"
												>
													{aTurno.comienza} <br />{aTurno.termina}
												</th>
												{#each aTurno.aSemanaTurnoPasadas as aSemana}
													<td
														class="text-center fs-6 align-middle p-1"
														style="max-width: 10rem; min-width: 10rem;"
													>
														{#each aSemana.aClases as aClase}
															<div
																class="card mb-3 p-3"
																style="max-width: 18rem; {aClase.style_card}"
															>
																<h5 class="card-title fs-5 fw-bold ">
																	{aClase.asignatura}
																</h5>
																<h6 class="card-title fs-6 fw-bold ">
																	{aClase.nivelmalla} - {aClase.paralelo}
																</h6>
																<p class="card-text p-0 m-0"><span>Aula: {aClase.aula}</span></p>
																<p class="card-text p-0 m-0"><span>Sede: {aClase.sede}</span></p>
																<p class="card-text p-0 m-0">
																	<span class="badge bg-secondary"
																		>{aClase.inicio} al {aClase.fin}</span
																	>
																</p>
																<p class="card-text p-0 m-0">
																	<span class="badge bg-info">{aClase.tipoprofesor}</span>
																</p>
																{#if aClase.profesor}
																	<div
																		class="card-text mt-1 badge bg-secondary text-wrap"
																		style="width: 10rem;"
																	>
																		{aClase.profesor}
																	</div>
																{/if}
																{#if aClase.grupoprofesor}
																	<p class="card-text p-0 m-0">
																		<span class="badge bg-info">{aClase.grupoprofesor}</span>
																	</p>
																{/if}
																<p class="card-text p-0 m-0">{aClase.tipohorario_display}</p>
															</div>
														{/each}
													</td>
												{/each}
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}

	{#if !isClasesActuales && !isClasesPasadas}
		<div class="alert alert-warning mt-4 text-center" role="alert">
			NO EXISTE REGISTRO DE CLASES PLANIFICADAS
		</div>
	{/if}
{:else}
	<div
		class="mt-4 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size={modalSize}
		on:actionRun={actionRun}
	/>
{/if}
