<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET, loadNotifications } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eConvenios = [];
		let next;
		let previous;
		let count;
		let limit;
		let vars_url;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/convenios', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				//console.log(errors);
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					if (!res.module_access) {
						return {
							status: 302,
							redirect: '/'
						};
					}
				} else {
					//console.log(res.data);
					eConvenios = res.data['convenios'];
					next = res.data['next'];
					previous = res.data['previous'];
					count = res.data['count'];
					limit = res.data['limit'];
					vars_url = res.data['vars_url'];
				}
			}
		}

		return {
			props: {
				eConvenios,
				next,
				previous,
				count,
				limit,
				vars_url
			}
		};
	};
</script>

<script lang="ts">
	import { loading } from '$lib/store/loadingStore';
	import { addNotification } from '$lib/store/notificationStore';
	import CollapsibleSection from './_collapsibleSection.svelte';

	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponenteCarreras from './_vercarreras.svelte';
	import ComponenteObjetivo from './_objetivo.svelte';
	import { navigating } from '$app/stores';
	import { onMount } from 'svelte';

	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	export let eConvenios;
	export let next;
	export let previous;
	export let count;
	export let limit;

	/* variables para filtro */
	export let estado;
	export let tipo;
	export let desde;
	export let hasta;
	export let search;
	export let vars_url;

	export let init_slide = 0;
	export let limit_slide = 7;

	/* varriables paginado */
	let url_pag = '';
	let page = 1;
	let offset = 0;
	
	/* botones de navegación */
	let deactive = true;
	let deactivenext = false;
	let deactivenav = true;
	let deactivenextnav = false;

	let num_pages = generatePages();
	
	/* variables modal */
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});

	/* Detalle Objetivo */
	const toggleModalDetalleObjetivo = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/convenios', {
			action: 'detalleobjetivo',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				//console.log(res.data);
				aDataModal = res.data;
				modalDetalleContent = ComponenteObjetivo;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Objetivo del Convenio';
			}
		}
	};

	/* ver carreras */
	const toggleModalVerCarreras = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/convenios', {
			action: 'vercarreras',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				//console.log(res.data);
				aDataModal = res.data;
				modalDetalleContent = ComponenteCarreras;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Programas';
			}
		}
	};

	const handleSearchReset = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/convenios', {});
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
				eConvenios = res.data['convenios'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
				search = res.data['search'];
				count = res.data['count'];
				desde = '';
				hasta = '';
				estado = '0';
				tipo = '0';
				offset = 0;
				page = 1;
				generatePages();
			}
			init_slide = 0;
			limit_slide = 7;
			validate_button();
			
		});
	};

	const handleSearh = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/convenios', {
				estado: estado,
				tipo: tipo,
				desde: desde,
				hasta: hasta,
				search: search
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
				eConvenios = res.data['convenios'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
				vars_url = res.data['vars_url'];
				offset = 0;
				page = 1;
			}
			init_slide = 0;
			limit_slide = count / limit;
			generatePages();
			validate_data_filtrered();
			validate_button();
		});
	};

	let pagination_function = async (term) => {
		let url_string = 'alumno/convenios';
		offset = limit * page;
		/* Pregunta por el boton presionado */
		if (term == 'next') {
			page += 1;
			//console.log('Page:' + page);
		} else if (term == 'prev') {
			page -= 1;
			offset = limit * page - limit;
			//console.log('Page:' + page);
		} else {
			page = term;
			offset = limit * page - limit;
			//console.log('Page:' + page);
		}
		/* Crea la url */
		url_pag = url_string + '?' + 'limit=' + limit + '&' + 'offset=' + offset + vars_url;
		//console.log(url_pag + '-' + page);

		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, url_pag, {});
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
				eConvenios = res.data['convenios'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
			}
			validate_data_filtrered();
			validate_button();
		});
	};

	/* Funcion Mostrar Data Limitada */
	let collapserdata = (indic) => {
		if (init_slide != 0) {
			if (indic == 'next') {
				init_slide += 7;
				limit_slide += 7;
				//console.log(init_slide + '--' + limit_slide);
				deactivenav = false;
				deactivenextnav = false;
				if (limit_slide >= num_pages.length - 1) {
					deactivenextnav = true;
				}
			} else {
				init_slide -= 7;
				limit_slide -= 7;
				deactivenav = true;
				deactivenav = false;
			}
		} else {
			if (indic == 'next') {
				init_slide += 7;
				limit_slide += 7;
				deactivenav = false;
				deactivenextnav = false;
				if (limit_slide >= num_pages.length - 1) {
					deactivenextnav = true;
				}
			} else {
				deactivenav = true;
				deactivenextnav = false;
			}
		}
	};

	function generatePages() {
		let num_pages = [];
		let limit_pages = count / limit;
		for (let i = 2; i < limit_pages + 1; i++) {
			num_pages.push(i);
		}
		return num_pages;
	}

	function validate_button() {
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
	}
	function validate_data_filtrered() {
		if (count == '0' || count < 20) {
			deactivenext = true;
			deactive = true;
		} else {
			deactivenext = false;
		}
	}
</script>

<!-- FILTROS -->
<div class="card mb-4">
	<div class="card-header border-bottom-1">
		<div class="d-md align-items-center">
			<form class="form-search">
				<div class="row-fluid">
					<div class="row ">
						<div class="col-lg-3 col-md-3 col-12">
							<div class="mb-3">
								<label for="selectestado" class="form-label"
									><i class="bi bi-card-list" /> Estados:</label
								>
								<select
									class="form-control"
									name="selectnotificacion"
									id="i_estado"
									style="width: 100%"
									bind:value={estado}
								>
									<option value="0">TODOS</option>
									<option value="1">VIGENTE</option>
									<option value="2">NO VIGENTE</option>
								</select>
							</div>
						</div>
						<div class="col-lg-3 col-md-3 col-12">
							<div class="mb-3">
								<label for="selecttipo" class="form-label"
									><i class="bi bi-card-list" /> Tipo:</label
								>
								<select
									class="form-control"
									name="selecttipo"
									id="i_tipo"
									style="width: 100%"
									bind:value={tipo}
								>
									<option value="0">TODOS</option>
									<option value="1">PARA PRÁCTICAS</option>
									<option value="2">PARA PASANTÍAS</option>
									<option value="3">PRÁCTICAS/PASANTÍAS</option>
								</select>
							</div>
						</div>

						<div class="col-lg-3 col-md-3 col-12">
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
						<div class="col-lg-3 col-md-3 col-12">
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
					</div>
					<div class="row">
						<div class="col-lg-12 col-md-12 col-12  ">
							<div class="mb-3">
								<label for="searchinput" class="form-label"
									><i class="bi bi-people " title="Estudiante" /> Criterio:</label
								>
								<div class="input-group">
									<input
										class="form-control"
										type="text"
										id="searchinput "
										bind:value={search}
										autocomplete="off"
										name="search"
										placeholder="Nombres Empresa, Tipo Convenio"
									/>
									<button
										class="btn btn-outline-primary"
										type="button"
										on:click|preventDefault={handleSearh}
										><i class="bi-search rounded-pill" /></button
									>
									<button
										class="btn btn-outline-warning"
										type="button"
										id="btnWarning"
										on:click|preventDefault={handleSearchReset}
										><i class="bi bi-arrow-repeat " /></button
									>
								</div>
							</div>
						</div>
					</div>
				</div>
			</form>
		</div>
	</div>
</div>

<!-- Data in table -->
<div class="row">
	<div class="col-lg-12 col-xm-12 col-md-12">
		<div class="card">
			<div class="card-body">
				<div class="table-responsive-lg">
					<table class="table mb-0 table-hover">
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;"
									>Cod. Convenio</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: auto"
									>Empresa</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: auto"
									>Tipo convenio</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;"
									>Inicio / Fin</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 10rem;"
									>Responsables interno / externo</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 12rem;"
									>Objetivo / archivos</th
								>
							</tr>
						</thead>
						<tbody>
							{#each eConvenios as convenio, i}
								<tr>
									<td class=" border-top-0 text-center align-middle ">
										<b> {i + 1} </b>
										<br />
										<label class="btn btn-dark btn-xs">Cod. {convenio.idm}</label>
									</td>
									<td class=" border-top-0 text-center align-middle">
										<label for="." class="form-label"> {convenio.empresaempleadora.nombre}</label>

										<br />
										<label class="btn btn-dark btn-xs">
											Cod. {convenio.empresaempleadora.idm}</label
										>

										{#if convenio.vigente == 'VIGENTE'}
											<a class="btn btn-success btn-xs">{convenio.vigente} </a>
										{:else}
											<a class="btn btn-secondary btn-xs">{convenio.vigente} </a>
										{/if}
										<!-- Tiene carreras ---- Abre modal -->
										{#if convenio.tienecarreras}
											<a
												class="btn btn-warning btn-xs m-1 label-mini "
												id={convenio.idm}
												on:click|preventDefault={() => toggleModalVerCarreras(convenio.id)}
												><i class="bi bi-journal-bookmark-fill" />
												PROGRAMAS - CARRERAS</a
											>
										{/if}
									</td>
									<td class=" border-top-0 text-center align-middle">
										{convenio.tipoconvenio.nombre}
									</td>
									<td class=" border-top-0 text-center align-middle">
										<label for="." class="form-label"> {convenio.fechainicio}</label>
										<label> / </label>
										<label for="." class="form-label"> {convenio.fechafinalizacion}</label>
									</td>

									<!-- Acordeon Mostrar mas menos -->
									<td class=" border-top-0 text-center align-middle">
										{#if convenio.responsables}
											<div class="accordion accordion-flush">
												{#each convenio.responsables as responsable}
													<CollapsibleSection
														headerText={'Cargo: ' + responsable.denominacionpuesto.display}
													>
														<div class="content ">
															<div class=" accordion-body">
																<b><i class="bi bi-person-fill" /> Resp. Interno</b>
																{responsable.persona.nombre_completo}
															</div>
														</div>
													</CollapsibleSection>
												{/each}
											</div>
										{:else}
											<label class="label form-label label-warning"> SIN RESPONSABLE INTERNO</label>
										{/if}
										<label class=""> <b>Ext: </b>{convenio.responsableexterno}</label>
									</td>
									<td class=" border-top-0 text-center align-middle">
										{#if convenio.archivosconvenio}
											<section>
												<CollapsibleSection headerText={'Archivos de convenio'}>
													<div class="content">
														<div>
															<ol>
																{#each convenio.archivosconvenio as archivo}
																	{#if archivo.archivo}
																		<li>
																			<b> CONVENIO: </b><br />
																			<a
																				title="Descargar archivo"
																				class="btn btn-success btn-xs rounded-pill"
																				href={archivo.download_link}
																				target="_blank"
																				data-fancybox-type="iframe"><i class="bi bi-download" /></a
																			>
																			<a
																				class="btn btn-primary btn-xs rounded-pill"
																				href={archivo.download_link}
																				target="_blank"
																			>
																				<i class="bi bi-file-pdf"> VER</i>
																			</a>
																		</li>
																	{/if}
																{/each}
															</ol>
														</div>
													</div>
												</CollapsibleSection>
											</section>
										{/if}

										<!-- Objetivo convenio a function -->
										{#if convenio.objetivo}
											<a
												id="detalle_objetivo"
												class="btn btn-primary btn-xs "
												on:click|preventDefault={() => toggleModalDetalleObjetivo(convenio.id)}
											>
												<span class="fa fa-comment" /> Objetivo del convenio</a
											>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>

		<div class="border-top-0">
			<div class="row my-3 px-3">
				<div class="col-lg-1 ">
					<nav>
						<ul class="pagination justify-content-left m-0">
							<li class="page-item">
								<button class="page-link btn rounded-pill readonly">
									{#if page != 0}
										<i class="bi bi-chevron" /> Pagina: {page}
									{:else}
										<i class="bi bi-chevron" /> Pagina: 1
									{/if}
								</button>
							</li>
						</ul>
					</nav>
				</div>
				<div class="col-lg-10 ">
					<nav>
						<ul class="pagination justify-content-center m-0">
							<li class="page-item">
								<button
									class="page-link btn rounded-pill"
									disabled={deactive}
									on:click|preventDefault={() => pagination_function('prev')}
								>
									<i class="bi bi-chevron-double-left" />
								</button>
							</li>

							{#if count > limit}
								<li class="page-item">
									<button
										class="page-link btn rounded-pill"
										disabled={deactivenav}
										on:click|preventDefault={() => collapserdata('prev')}
									>
										<i class="bi bi-chevron" />
										-
									</button>
								</li>

								{#each num_pages.slice(init_slide, limit_slide) as num}
									<li class="page-item">
										<button
											class="page-link btn rounded-pill"
											on:click|preventDefault={() => pagination_function(num)}
										>
											<i class="bi bi-chevron" />
											{num}
										</button>
									</li>
								{/each}

								<li class="page-item">
									<button
										class="page-link btn rounded-pill"
										disabled={deactivenextnav}
										on:click|preventDefault={() => collapserdata('next')}
									>
										<i class="bi bi-chevron" />
										+
									</button>
								</li>
							{/if}

							<li class="page-item">
								<button
									class="page-link btn  rounded-pill"
									disabled={deactivenext}
									on:click|preventDefault={() => pagination_function('next')}
								>
									<i class="bi bi-chevron-double-right" />
								</button>
							</li>
						</ul>
					</nav>
				</div>
			</div>
		</div>		
	</div>
</div>

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
	/>
{/if}
