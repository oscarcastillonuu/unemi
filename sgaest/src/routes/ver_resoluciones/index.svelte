<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eResoluciones = [];
		let eTipoResoluciones = [];
		let items_tipo_resoluciones = [];
		let item_tipo_resolucion = {};
		let search;
		let previous;
		let next;
		let count;
		let url_vars;

		const ds = browserGet('dataSession');
		console.log(ds + 'DataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/resoluciones', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				console.log('ResDATA:' + res.data);
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
								//console.log(res.message);
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							//console.log(res.message);
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						//console.log(res.message);
					}
				} else {
					//console.log(res.data);
					eResoluciones = res.data['eResoluciones'];
					eTipoResoluciones = res.data['eTipoResoluciones'];
					search = res.data['search'];
					previous = res.data['previous'];
					next = res.data['next'];
					count = res.data['count'];
					url_vars = res.data['url_vars'];
					for (const i in eTipoResoluciones) {
						item_tipo_resolucion = {
							value: eTipoResoluciones[i]['id'],
							label: eTipoResoluciones[i]['nombre']
						};
						items_tipo_resoluciones.push({
							value: eTipoResoluciones[i]['id'],
							label: eTipoResoluciones[i]['nombre']
						});
					}
				}
			}
		}
		return {
			props: {
				eResoluciones,
				eTipoResoluciones,
				item_tipo_resolucion,
				items_tipo_resoluciones,
				search,
				previous,
				next,
				count
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { navigating } from '$app/stores';
	// import Select from 'svelte-select/Select.svelte'; //https://github.com/rob-balfre/svelte-select

	export let eResoluciones;
	export let eTipoResoluciones;
	export let item_tipo_resolucion;
	export let items_tipo_resoluciones;
	export let search;
	export let desde;
	export let hasta;
	export let tipoRes;
	export let url_vars;
	export let next;
	export let previous;
	export let count;
	export let init_slide = 0;
	export let limit_slide = 20;

	let url_nav = '';
	let page = 1;
	let new_limit = 0;
	let limit = 20;
	let offset = 0;
	let deactive = true;
	let deactivenext = false;

	export let id_tipoResolucion = 0;

	let itemsBreadCrumb = [{ text: 'Resoluciones', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		id_tipoResolucion = item_tipo_resolucion ? item_tipo_resolucion.value : 0;
	});

	/* Buscar Por Formulario*/
	const handleSearch2 = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/resoluciones', {
				tipore: id_tipoResolucion,
				search: search,
				desde: desde,
				hasta: hasta
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				reject({
					error: true,
					message: errors[0].error
				});
			} else {
				resolve({
					error: false,
					value: res.data
				});
				//console.log(res);
				eResoluciones = res.data['eResoluciones'];
				eTipoResoluciones = res.data['eTipoResoluciones'];
				search = res.data['search'];
				count = res.data['count'];
				offset = 0;
				page = 1;
			}
			if (count == '0' || count < 20) {
				deactivenext = true;
				deactive = true;
			} else {
				deactivenext = false;
			}
		});		
	};
	/* Buscar todos - Resetar Busqueda */
	const handleSearch = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/resoluciones', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				reject({
					error: true,
					message: errors[0].error
				});
			} else {
				resolve({
					error: false,
					value: res.data
				});
				eResoluciones = res.data['eResoluciones'];
				eTipoResoluciones = res.data['eTipoResoluciones'];
				search = res.data['search'];
				url_vars = res.data['url_vars'];
				count = res.data['count'];
				desde = '';
				hasta = '';
				offset = 0;
				page = 1;
			}
			if (count == '0' || count < 20) {
				deactivenext = true;
				deactive = true;
			} else {
				deactivenext = false;
			}
		});
	};

	/* Ver mas, ver menos */
	let mycollapsemore = (valor, id) => {
		let spancompleted = document.getElementById(id);
		let id_string = 'spanvermas_' + id;
		let id_ver_menos = 'spanvermenos_' + id;
		let spanvermas = document.getElementById(id_string);
		let spanvermenos = document.getElementById(id_ver_menos);
		let v_mas_menos = valor;
		if (v_mas_menos) {
			spancompleted.style.display = '';
			spanvermas.style.display = 'none';
			spanvermenos.style.display = '';
		} else {
			spancompleted.style.display = 'none';
			spanvermas.style.display = '';
			spanvermenos.style.display = 'none';
		}
	};

	/* Funcion Mostrar Data Limitada */
	let collapserdata = (indic) => {
		console.log(eResoluciones.length);

		if (init_slide != 0) {
			if (indic == 'next') {
				init_slide += 20;
				limit_slide += 20;
				console.log(init_slide + '--' + limit_slide);
				console.log(eResoluciones.slice);
			} else {
				init_slide -= 20;
				limit_slide -= 20;
				console.log(init_slide + '--' + limit_slide);
				console.log(eResoluciones.slice);
			}
		} else {
			if (indic == 'next') {
				init_slide += 20;
				limit_slide += 20;
				console.log(init_slide + '--' + limit_slide);
				console.log(eResoluciones.slice);
			} else {
				console.log('ELSE init = 0');
			}
		}
	};

	/* Funcion paginado */
	let navigation = async (term) => {
		let string = 'alumno/resoluciones';
		offset = limit * page;
		/* Pregunta por el boton presionado */
		if (term == 'next') {
			new_limit = offset + limit;
			page += 1;
		} else {
			new_limit = offset - limit;
			page -= 1;
			offset = limit * page - limit;
		}
		/* Crea la url */
		url_nav = string + '?' + 'limit=' + limit + '&' + 'offset=' + offset;
		//console.log(url_nav);
		/* Realiza consulta a la base */
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, url_nav, {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				reject({
					error: true,
					message: errors[0].error
				});
			} else {
				resolve({
					error: false,
					value: res.data
				});
				//console.log(res.data);
				eResoluciones = res.data['eResoluciones'];
				eTipoResoluciones = res.data['eTipoResoluciones'];
				search = res.data['search'];
				desde = '';
				hasta = '';
				previous = res.data['previous'];
				next = res.data['next'];
				count = res.data['count'];
				url_vars = res.data['url_vars'];
			}
		});
		/* Validacion para desactivar botones */
		if (offset > 0) {
			deactive = false;
		} else {
			deactive = true;
		}
		if (next == null) {
			deactivenext = true;
		} else {
			deactivenext = false;
		}
	};

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
</script>

<svelte:head>
	<title>Resoluciones</title>
</svelte:head>
{#if load}
	<BreadCrumb title="Resoluciones" items={itemsBreadCrumb} back={backBreadCrumb} />
	<!-- Formulario -->
	<div class="card mb-4">
		<div class="card-header border-bottom-1">
			<div class="d-md align-items-center">
				<div class="row-fluid">
					<div class="row ">
						<div class="col-12">
							<form class="form-search">
								<div class="col-lg-12 col-md-12 col-12">
									<div class="mb-3">
										<label for="id_tipore" class="form-label"
											><i class="bi bi-card-list" /> Tipos:</label
										>
										<select
											class="form-control"
											name="tipore"
											id="id_tipore"
											style="width: 100%"
											bind:value={id_tipoResolucion}
											on:change={handleSearch2}
										>
											<option value="0">TODOS</option>
											{#each eTipoResoluciones as tipoRes}
												<option value={tipoRes.id}>
													{tipoRes.nombre}
												</option>
											{/each}
										</select>
									</div>
								</div>
							</form>
						</div>
					</div>
					<div class="row ">
						<div class="col-lg-2 col-md-3 col-12">
							<div class="mb-3">
								<label for="desde" class="form-label"
									><i class="bi bi-calendar-minus" title="Desde" /> Desde:</label
								>
								<input
									class="form-control"
									type="date"
									id="desde"
									bind:value={desde}
									autocomplete="off"
									style="width: 100%"
									name="desde"
								/>
							</div>
						</div>
						<div class="col-lg-2 col-md-3 col-12">
							<div class="mb-3">
								<label for="hasta" class="form-label"
									><i class="bi bi-calendar-minus" title="Hasta" /> Hasta:</label
								>

								<input
									class="form-control"
									type="date"
									id="hasta"
									bind:value={hasta}
									autocomplete="off"
									style="width: 100%"
									name="hasta"
								/>
							</div>
						</div>
						<div class="col-lg-8 col-md-6 col-12  ">
							<div class="mb-3">
								<label for="searchinput" class="form-label"
									><i class="bi bi-people " title="Estudiante" /> Resolución:</label
								>
								<div class="input-group">
									<input
										class="form-control"
										type="text"
										id="searchinput "
										bind:value={search}
										autocomplete="off"
										name="search"
										placeholder="Número de Resolucion, Resuelve"
									/>
									<button
										class="btn btn-outline-primary"
										type="button"
										on:click|preventDefault={handleSearch2}
										><i class="bi-search rounded-pill" /></button
									>
									<button class="btn btn-outline-warning" type="button" id="btnWarning" on:click|preventDefault={handleSearch}><i class="bi bi-arrow-repeat " /></button>
									<!--<span class="input-group-text"
										><a
											id="search"
											type="button"
											class="btn btn-link rounded-pill m-0 p-0"
											on:click|preventDefault={handleSearch2}
											><i class="bi-search rounded-pill" />
										</a></span
									>
									<span class="input-group-text"
										><a
											id="allresults"
											class="btn btn-link rounded-pill m-0 p-0"
											on:click|preventDefault={handleSearch}
											><span class="bi bi-arrow-repeat " />
										</a></span
									>-->
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<!-- Datos -->
	<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4">
		{#each eResoluciones as resolucion}
			<div class="col">
				<div class="card h-100">
					<div class="card-body">
						<div class="d-flex align-items-center justify-content-between ">
							<div>
								<h4 class="mb-0" style="text-align: center">
									<b>{resolucion.numeroresolucion}</b>
								</h4>
							</div>
						</div>
						<div class="mt-3 mb-4 card-text">
							<p class="mb-0"><b>Resuelve: </b></p>
							<p style="text-align: justify">
								<span id="span" class="parte1_{resolucion.id}"
									>{resolucion.resuelve.slice(0, 102)}</span
								>
								<span
									id={resolucion.id}
									class="parte2 hidden_{resolucion.id} "
									style="display: none;">{resolucion.resuelve.slice(102)}</span
								>
								{#if resolucion.resuelve.length >= 102}
									<span
										id="spanvermas_{resolucion.id}"
										class="mycollapsemore badge"
										on:click={() => mycollapsemore(true, resolucion.id)}
										style="border:1px solid rgba(157, 157, 157, 0.55);border-radius:10px;color:black;font-weight: normal;background-color: #fff;cursor:pointer;"
										>Ver más
									</span>
									<span
										id="spanvermenos_{resolucion.id}"
										class="mycollapsemore badge"
										on:click={() => mycollapsemore(false, resolucion.id)}
										style="display: none; border:1px solid rgba(157, 157, 157, 0.55);border-radius:10px;color:black;font-weight: normal;background-color: #fff;cursor:pointer;"
										>Ver menos
									</span>
								{:else}
									<br />
								{/if}
							</p>
						</div>
					</div>
					<div class="card-footer bg-white p-0">
						<div class="d-flex justify-content-between ">
							<div class="w-50 py-3 px-4 ">
								<h6 class="mb-0 text-muted">Fecha de inicio:</h6>
								<p class="text-dark fs-6 fw-semi-bold mb-0">{resolucion.fecha.slice(0, 10)}</p>
							</div>
							<div class="border-start w-50 py-3 px-4">
								<div style="text-align: center">
									<a
										class="btn btn-warning rounded-pill"
										href={resolucion.download_link}
										target="_blank"
										data-fancybox-type="iframe"><i class="bi bi-download" /></a
									>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>
	<!-- Paginado -->
	<div class="border-top-0">
		<div class="row my-3 px-3">
			<div class="col-lg-12 gridjs-pagination">
				<nav>
					<ul class="pagination justify-content-center m-0">
						<li class="page-item">
							<button
								class="page-link btn rounded-pill"
								disabled={deactive}
								on:click={() => navigation('prev')}
							>
								<i class="bi bi-chevron-double-left" />
							</button>
						</li>
						<li class="page-item">
							<button
								class="page-link btn  rounded-pill"
								disabled={deactivenext}
								on:click={() => navigation('next')}
							>
								<i class="bi bi-chevron-double-right" />
							</button>
						</li>
					</ul>
				</nav>
			</div>
		</div>
	</div>
{/if}
