<script lang="ts">
	import { goto } from '$app/navigation';
	import moment from 'moment';
	import { loading } from '$lib/store/loadingStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { addToast } from '$lib/store/toastStore';
	import { apiGET, apiPOST } from '$lib/utils/requestUtils';
	import { onDestroy, onMount } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import { Icon, Spinner } from 'sveltestrap';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import ComponentViewUbicacion from './_modal/ubicacion.svelte';
	export let eMateriaAsignada;
	export let eMatriculaSedeExamen;
	let tiene_fase_2 = false;
	let horarioexamendetallealumno = [];
	let planificacionsede = [];
	let disertaciones = [];
	let clientNavegador;
	let clientOS;
	let clientScreensize;
	let btnAccesoExamen = false;
	let load = true;
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModal = false;
	let mTitle = '';
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down';
	let mSizeModal = 'xl';
	const mToggleModal = () => (mOpenModal = !mOpenModal);

	const DEBUG = variables;
	let interval;
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		clienteInfo(window);

		horarioexamendetallealumno = (await eMateriaAsignada.horarioexamendetallealumno) ?? [];
		disertaciones = (await eMateriaAsignada.disertaciones) ?? [];
		planificacionsede = (await eMateriaAsignada.planificacionsede) ?? [];

		//can_reload = true;
		//await loadMateriaAsignada();
		if (eMatriculaSedeExamen) {
			tiene_fase_2 = eMatriculaSedeExamen.tiene_fase_2 ?? false;
		}
		load = false;
		//await loadMateriaAsignada2();
		//await loadMateriaAsignada3();
		/*if (tiene_fase_2) {
			
		}*/

		await loadInterval();
		interval = setInterval(function () {
			loadInterval();
		}, 1000);
	});

	onDestroy(() => {
		if (interval) {
			console.log('clearInterval');
			clearInterval(interval);
		}
	});

	const loadAjax = async (data, url, method = undefined) =>
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
				const [res, errors] = await apiPOST(fetch, url, data);
				//console.log(errorsCertificates);
				if (errors.length > 0) {
					reject({
						error: true,
						message: errors[0].error
					});
				} else {
					resolve({
						error: false,
						value: res
					});
				}
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
				//console.log(errorsCertificates);
				if (errors.length > 0) {
					reject({
						error: true,
						message: errors[0].error
					});
				} else {
					resolve({
						error: false,
						value: res
					});
				}
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

	const GuardarAsistenciaExamen = async (id, idExamen, detalle) => {
		// window.open(urlprofesor, '_blank');
		//clearInterval(interval);
		//goto('/');
		var  urlprofesor =  null;
		console.log(detalle.tiporesponsable)
		if(detalle.tiporesponsable === 1 && detalle.profesormateria){
			urlprofesor = detalle.profesormateria.profesor.urlzoom
		} else if (detalle.tiporesponsable === 2 && detalle.profesor){
			urlprofesor = detalle.profesor.urlzoom
		}
		if (urlprofesor === '' || urlprofesor === null) {
			addNotification({
				msg: 'Url de profesor no configurada',
				type: 'error'
			});
			return false;
		}

		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'addcliczoom',
				id: id,
				idExamen: idExamen,
				navegador: clientNavegador,
				os: clientOS,
				screensize: clientScreensize
			},
			'alumno/aulavirtual'
		)
			.then((response) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (response.value.isSuccess) {
					addNotification({
						msg: 'Se guardó la asistencia a su examen.',
						type: 'info'
					});
					setTimeout(function() {
						window.open(urlprofesor, '_blank');
					}, 1000);
				} else {
					addNotification({
						msg: response.value.message,
						type: 'error'
					});
					setTimeout(function() {
						window.open(urlprofesor, '_blank');
					}, 1000);
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};

	const loadInterval = async () => {
		//if (can_reload) {

		//}
		horarioexamendetallealumno.forEach(async (horario) => {
			await esta_disponible_exa_1(horario);
		});
	};

	const loadMateriaAsignada = async () => {
		load = true;
		//can_reload = false;
		//loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual/examenes', {
			action: 'loadMateriaAsignadaHorarioExamen',
			id: eMateriaAsignada.id
		});
		//loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				//console.log(res.data);
				horarioexamendetallealumno = res.data['horarioexamendetallealumno'];
			}
			//can_reload = true;
		}
		load = false;
	};
	const loadMateriaAsignada2 = async () => {
		load = true;
		//can_reload = false;
		//loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual/examenes', {
			action: 'loadPlanificacionSedeExamen',
			id: eMateriaAsignada.id
		});
		//loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				//console.log(res.data);
				planificacionsede = res.data['planificacionsede'];
			}
			//can_reload = true;
		}
		load = false;
	};

	const loadMateriaAsignada3 = async () => {
		load = true;
		//can_reload = false;
		//loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual/examenes', {
			action: 'loadPlanificacionDisertacion',
			id: eMateriaAsignada.id
		});
		//loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				//console.log(res.data);
				disertaciones = res.data['disertaciones'];
			}
			//can_reload = true;
		}
		load = false;
	};

	const esta_disponible_exa_1 = async (horario) => {
		//console.log("# horario.horarioexamendetalle.tiporesponsable: ", horario.horarioexamendetalle.tiporesponsable);
		const elmentBtn = document.getElementById(`btn_id_${horario.id}`);
		//elmentBtn.style.display = 'none';
		let urlzoom = null;
		if(horario.horarioexamendetalle.tiporesponsable === 1 && horario.horarioexamendetalle.profesormateria){
			urlzoom = horario.horarioexamendetalle.profesormateria.profesor.urlzoom
		} else if (horario.horarioexamendetalle.tiporesponsable === 2 && horario.horarioexamendetalle.profesor){
			urlzoom = horario.horarioexamendetalle.profesor.urlzoom
		}
		if (elmentBtn != undefined) {
			elmentBtn.style.display = 'none';
			if (
				//horario.horarioexamendetalle.tiporesponsable != 1 ||
				//horario.horarioexamendetalle.aula.idm != 218 ||
				//horario.horarioexamendetalle.horarioexamen.detallemodelo.nombre != 'EX1' ||
				urlzoom === undefined || urlzoom === ''
				
			) {
				elmentBtn.style.display = 'none';
			}

			if (
				horario.horarioexamendetalle.horarioexamen.fecha === undefined ||
				//horario.horarioexamendetalle.horarioexamen.fecha === '' ||
				horario.horarioexamendetalle.horainicio === undefined ||
				//horario.horarioexamendetalle.horainicio === '' ||
				horario.horarioexamendetalle.horafin === undefined ||
				//horario.horarioexamendetalle.horafin === '' ||
				horario.fecha_actual === undefined ||
				//horario.fecha_ahora === '' ||
				horario.hora_actual === undefined
				//horario.hora_ahora === ''
			) {
				elmentBtn.style.display = 'none';
			}
			//console.log("# if: ", 2);
			//console.log("fecha_actual: ", horario.fecha_actual);
			//console.log("fecha: ", horario.horarioexamendetalle.horarioexamen.fecha);
			let fecha = moment().format('YYYY-MM-DD');
			let fecha_actual = moment().format('YYYY-MM-DD');
			fecha_actual = moment(`${horario.fecha_actual}`).format('YYYY-MM-DD');
			fecha = moment(`${horario.horarioexamendetalle.horarioexamen.fecha}`).format('YYYY-MM-DD');
			/*console.log('fecha: ', fecha);
			console.log('fecha_actual: ', fecha_actual);
			console.log('igual: ', moment(fecha).isSame(fecha_actual));
			console.log('DEBUG: ', DEBUG);*/
			//console.log("fecha: ", horario.horarioexamendetalle.horarioexamen.fecha);
			if (moment(fecha_actual).isSame(fecha)) {
				elmentBtn.style.display = 'block';
				let ahora = moment(new Date()).format('YYYY-MM-DD HH:mm:ss');
				let fin = moment(
					`${horario.horarioexamendetalle.horarioexamen.fecha} ${horario.horarioexamendetalle.horafin}`,
					'YYYY-MM-DD HH:mm:ss'
				);
				let inicio = moment(
					`${horario.horarioexamendetalle.horarioexamen.fecha} ${horario.horarioexamendetalle.horainicio}`,
					'YYYY-MM-DD HH:mm:ss'
				);
				/*if (DEBUG){
					ahora = moment('2022-07-22 19:00:01', 'YYYY-MM-DD HH:mm:ss');
					inicio = moment('2022-07-22 19:00:00', 'YYYY-MM-DD HH:mm:ss');
					fin = moment('2022-07-22 20:59:59', 'YYYY-MM-DD HH:mm:ss');
				}
				console.log("inicio: ", ahora.isAfter(inicio));
				console.log("fin: ", ahora.isBefore(fin));
				
				if (ahora.isAfter(inicio) && ahora.isBefore(fin)){
					elmentBtn.style.display = 'block';
				}*/
				inicio = inicio.subtract(15, 'minutes');
				if (
					ahora >= inicio.format('YYYY-MM-DD HH:mm:ss') &&
					ahora <= fin.format('YYYY-MM-DD HH:mm:ss')
				) {
					elmentBtn.style.display = 'block';
				} else {
					elmentBtn.style.display = 'none';
				}
			} else {
				elmentBtn.style.display = 'none';
			}
		}
	};

	const generateCodigoQR = async (eMateriaAsignadaPlanificacionSedeVirtualExamen) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual/examenes', {
			action: 'generateCodigoQRMateriaAsignadaHorarioExamen',
			id: eMateriaAsignadaPlanificacionSedeVirtualExamen.id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				loading.setLoading(true, 'Cargando, espere por favor...');
				addToast({ type: 'success', header: 'Exitoso', body: res.message });
				var a = document.createElement('a');
				a.target = '_blank';
				a.href = res.data.url_pdf;
				a.click();
				await delay(1000);
				window.location.reload();
			}
		}
	};

	const registreAsistenciaDisertacion = async (eDisertacionMateriaAsignadaPlanificacion) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual/examenes', {
			action: 'registreDisertacionMateriaAsignada',
			id: eDisertacionMateriaAsignadaPlanificacion.id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			goto('/');
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
			} else {
				loading.setLoading(true, 'Cargando, espere por favor...');
				addToast({ type: 'success', header: 'Exitoso', body: res.message });
				var a = document.createElement('a');
				a.target = '_blank';
				a.href = res.data.link_meet;
				a.click();
				await delay(1000);
				// window.location.reload();
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		}
	};
	async function copiarClave() {
		const informacion = document.getElementById('clave_examen');
		const texto = informacion.innerText;
		try {
			await navigator.clipboard.writeText(texto);
			//alert(' copiada!');
		} catch (error) {
			console.error('No se pudo copiar la información', error);
		}
	}

	async function irMeet(url) {
		window.open(url, '_blank');
	}

	const view_pdf = (url) => {
		aDataModal = { url: url };
		modalDetalleContent = ComponentViewPDF;
		mOpenModal = !mOpenModal;
		mTitle = 'Ver pdf';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};

	const actionRun = (event) => {
		//mOpenModal2 = false;
		//loading.setLoading(false, 'Cargando, espere por favor...');
		const detail = event.detail;
		const action = detail.action;
	};

	const openUbicacionAula = (eBloque) => {
		aDataModal = { eBloque: eBloque };
		modalDetalleContent = ComponentViewUbicacion;
		mOpenModal = !mOpenModal;
		mTitle = 'Ver ubicación';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};
</script>

{#if !load}
	{#if horarioexamendetallealumno.length > 0 || planificacionsede.length > 0 || disertaciones.length > 0}
		<div class="row row-cols-1 g-4" style="--bs-gutter-x: 0.5rem;">
			{#each horarioexamendetallealumno as horario}
				<div class="col">
					<div class="card h-100 m-0 p-2 border border-2 shadow-none">
						<div class="d-flex align-items-center">
							<div class="m-2">
								<h4 class="mb-0 nompersonas">
									{horario.horarioexamendetalle.horarioexamen.detallemodelo.display}
								</h4>
								<p class="mb-0 texto-naranja fs-6">
									<b>{horario.horarioexamendetalle.horarioexamen.fecha}</b> desde
									<b>{horario.horarioexamendetalle.horainicio}</b>
									hasta <b>{horario.horarioexamendetalle.horafin}</b>
								</p>

								{#if horario.horarioexamendetalle.tiporesponsable === 1}
									<p class="mb-0 text-muted">
										Responsable <b
											>{horario.horarioexamendetalle.profesormateria.profesor.persona
												.nombre_completo}</b
										>
									</p>
								{:else if horario.horarioexamendetalle.tiporesponsable === 2}
									<p class="mb-0 text-muted">
										Responsable <b
											>{horario.horarioexamendetalle.profesor.persona.nombre_completo}</b
										>
									</p>
								{:else if horario.horarioexamendetalle.tiporesponsable === 3}
									<p class="mb-0 text-muted">
										Responsable <b
											>{horario.horarioexamendetalle.administrativo.persona.nombre_completo}</b
										>
									</p>
								{/if}
								<p class=" border-top pt-1 m-0">
									{#if horario.horarioexamendetalle.aula}
										Aula:<b>{horario.horarioexamendetalle.aula.nombre}</b>
										{#if horario.horarioexamendetalle.aula.bloque}
											Bloque: <b>{horario.horarioexamendetalle.aula.bloque.descripcion}</b>
										{/if}
									{:else}
										Aula: <b>Por definir</b>
										Bloque: <b>Por definir</b>
									{/if}
								</p>
								<button
									on:click={() =>
										GuardarAsistenciaExamen(
											eMateriaAsignada.id,
											horario.horarioexamendetalle.horarioexamen.id,
											horario.horarioexamendetalle
										)}
									id="btn_id_{horario.id}"
									style="display: none;"
									class="btn btn-success rounded-pill btn-sm py-2"
								>
									<i class="bi bi-camera-video" /> Ir a Meet
								</button>
							</div>
						</div>
					</div>
				</div>
			{/each}
			<!--{#if tiene_fase_2}-->
			{#each planificacionsede as pla}
				<div class="col">
					<div class="card h-100 m-0 p-2 border border-2 shadow-none">
						<div class="d-flex align-items-center">
							{#if pla.utilizar_qr}
								{#if tiene_fase_2}
									{#if pla.url_qr}
										<div class="m-2">
											<h4 class="mb-0 nompersonas text-center text-info fw-bold">
												{pla.detallemodeloevaluativo.display}
											</h4>
											<p class="mb-0 text-center">
												<b>{pla.aulaplanificacion.turnoplanificacion.fechaplanificacion.fecha}</b>
												desde
												<b>{pla.aulaplanificacion.turnoplanificacion.horainicio}</b>
												hasta <b>{pla.aulaplanificacion.turnoplanificacion.horafin}</b>
											</p>
											{#if pla.aulaplanificacion.turnoplanificacion.fechaplanificacion.sede}
												<p class="mb-0">
													<b>Sede:</b>
													<span class="text-warning"
														>{pla.aulaplanificacion.turnoplanificacion.fechaplanificacion.sede
															.nombre}</span
													>
												</p>
											{/if}

											{#if pla.aulaplanificacion.aula.bloque}
												<p class="mb-0">
													<b>Bloque: </b>
													<a
														href="#{pla.aulaplanificacion.aula.bloque.id}"
														class="btn-mini btn-link p-0 m-0"
														on:click|preventDefault={() =>
															openUbicacionAula(pla.aulaplanificacion.aula.bloque)}
														><Icon name="geo-alt-fill" />
														{pla.aulaplanificacion.aula.bloque.descripcion}</a
													>
												</p>
											{/if}
											<p class="p-0 m-0">
												<b>{pla.aulaplanificacion.aula.tipo.nombre}:</b>
												{pla.aulaplanificacion.aula.nombre}
											</p>

											{#if pla.aulaplanificacion.responsable}
												<p class="mb-0 text-muted">
													Responsable <b>{pla.aulaplanificacion.responsable.nombre_completo}</b>
												</p>
											{/if}
											 <!-- {#if pla.aulaplanificacion.turnoplanificacion.id === 'OPPQQRRSSTTUUVVWUOQW'}
												<p class="p-0 m-0">
													<b>Clave de acceso al examen:</b>
													<span id="clave_examen">{pla.password}</span>
												</p>
												<button class="btn btn-info btn-xs" on:click={copiarClave}>
													<i class="bi bi-clipboard"> Copiar Clave</i>
												</button>
											{/if}-->
											{#if pla.aulaplanificacion.responsable && pla.puede_ir_meet}
												<button
													class="btn btn-success rounded-pill btn-sm py-2"
													on:click={() => irMeet(pla.url_profesor)}
												>
													<i class="bi bi-camera-video" /> Ir a Meet
												</button>
											{/if}
											<div class="text-center mt-1">
												<button
													class="btn btn-primary rounded-pill btn-sm py-2 "
													on:click={() => view_pdf(pla.url_qr)}
												>
													Ver Código QR <i class="bi bi-qr-code" />
												</button>
												<button
													class="btn btn-danger rounded-pill btn-sm py-2 "
													on:click={() => generateCodigoQR(pla)}
												>
													Generar Código QR <i class="bi bi-gear" />
												</button>
											</div>
										</div>
									{:else}
										<div class="m-2">
											<h4 class="mb-0 ">{pla.detallemodeloevaluativo.display}</h4>

											<button
												class="btn btn-danger rounded-pill btn-sm py-2 "
												on:click={() => generateCodigoQR(pla)}
											>
												<i class="bi bi-refresh"> Generar Código QR</i>
											</button>
										</div>
									{/if}
								{:else}
									<div class="m-2">
										<h5 class="text-center text-primary">
											No puede visualizar el horario porque no ha aceptado el acuerdo de terminos y
											condiciones de exámenes finales
										</h5>
									</div>
								{/if}
							{:else}
								<div class="m-2">
									<h4 class="mb-0 nompersonas">{pla.detallemodeloevaluativo.display}</h4>
									<p class="mb-0 texto-naranja">
										<b>{pla.aulaplanificacion.turnoplanificacion.fechaplanificacion.fecha}</b>
										desde
										<b>{pla.aulaplanificacion.turnoplanificacion.horainicio}</b>
										hasta <b>{pla.aulaplanificacion.turnoplanificacion.horafin}</b>
									</p>
									{#if pla.aulaplanificacion.responsable}
										<p class="mb-0 text-muted">
											Responsable <b>{pla.aulaplanificacion.responsable.nombre_completo}</b>
										</p>
									{/if}

									<p class="p-0 m-0">
										<b>{pla.aulaplanificacion.aula.tipo.nombre}:</b>
										{pla.aulaplanificacion.aula.nombre}
									</p>

									 <!-- {#if pla.aulaplanificacion.turnoplanificacion.id === 'OPPQQRRSSTTUUVVWUOQW'}
										<p class="p-0 m-0">
											<b>Clave de acceso al examen:</b>
											<span id="clave_examen">{pla.password}</span>
										</p>
										<button class="btn btn-info btn-xs" on:click={copiarClave}>
											<i class="bi bi-clipboard"> Copiar Clave</i>
										</button>
									 {/if}--> 
									{#if pla.aulaplanificacion.responsable && pla.puede_ir_meet}
										<button
											class="btn btn-success rounded-pill btn-sm py-2"
											on:click={() => irMeet(pla.url_profesor)}
										>
											<i class="bi bi-camera-video" /> Ir a Meet
										</button>
									{/if}
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/each}
			{#each disertaciones as disertacion}
				<div class="col">
					<div class="card h-100 m-0 p-2 border border-2 shadow-none">
						<div class="d-flex align-items-center">
							<div class="m-2">
								<h4 class="mb-0 nompersonas ">
									{disertacion.grupoplanificacion.detallemodeloevaluativo.display}
								</h4>
								<p class="mb-0 texto-naranja">
									<b
										>{disertacion.grupoplanificacion.aulaplanificacion.turnoplanificacion
											.fechaplanificacion.fecha}</b
									>
									desde
									<b
										>{disertacion.grupoplanificacion.aulaplanificacion.turnoplanificacion
											.horainicio}</b
									>
									hasta
									<b
										>{disertacion.grupoplanificacion.aulaplanificacion.turnoplanificacion
											.horafin}</b
									>
								</p>
								{#if disertacion.grupoplanificacion.responsable}
									<p class="mb-0 text-muted">
										Responsable <b>{disertacion.grupoplanificacion.responsable.nombre_completo}</b>
									</p>
								{/if}

								<p class="p-0 m-0">
									<b>{disertacion.grupoplanificacion.aulaplanificacion.aula.tipo.nombre}:</b>
									{disertacion.grupoplanificacion.aulaplanificacion.aula.nombre}
								</p>
								{#if disertacion.puede_ingresar}
									{#if disertacion.grupoplanificacion.link_meet}
										<button
											class="btn btn-primary rounded-pill btn-sm py-2 "
											on:click={() => registreAsistenciaDisertacion(disertacion)}
										>
											Ingresar a disertar <i class="bi bi-clock" />
										</button>
									{:else}
										<p class="text-warning">Responsable no registra enlace de meet</p>
									{/if}
								{/if}
							</div>
						</div>
					</div>
				</div>
			{/each}
			<!--{/if}-->
		</div>
	{:else}
		<p class="text-center text-primary">NO EXISTE EXAMENES DISPONIBLES</p>
	{/if}
{:else}
	<div class="col-auto text-center">
		<Spinner color="primary" type="border" style="width: 2rem; height: 2rem;" />
		<h5>Verificando la información, espere por favor...</h5>
	</div>
{/if}

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		{mOpenModal}
		{mTitle}
		aData={aDataModal}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
{/if}

<style>
	.texto-naranja {
		color: #fe9900;
	}
</style>
