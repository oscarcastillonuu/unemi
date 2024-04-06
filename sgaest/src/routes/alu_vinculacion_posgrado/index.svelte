<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eVinculacionPosgrado = [];
		let next;
		let previous;
		let count;
		let limit;
		let is_error = false;
		let messageError = undefined;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const [res, errors] = await apiGET(fetch, 'alumno/alu_vinculacion_posgrado', {
				action: 'list'
			});
			if (errors.length > 0) {
				is_error = true;
				messageError = errors[0].error;
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					is_error = true;
					messageError = res.message;
				} else {
					is_error = false;
					console.log(res.data['listado']);
					eVinculacionPosgrado = res.data['listado'];
					next = res.data['next'];
					previous = res.data['previous'];
					count = res.data['count'];
					limit = res.data['limit'];
				}
			}
		}
		return {
			props: {
				eVinculacionPosgrado,
				next,
				previous,
				count,
				limit
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { Spinner } from 'sveltestrap';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponenteDetalleProyectoVinculacion from './_detalle_proyecto_vinculacion.svelte';
	import ComponenteFormProyectoVinculacion from './_formproyectovinculacion.svelte';

	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
	import ModuleError from '../__error.svelte';
	import { h, html } from 'gridjs';
	export let is_error;
	let load = true;

	/* Data exportada */
	export let eVinculacionPosgrado;
	export let next;
	export let previous;
	export let count;
	export let limit;

	/* variables para filtro */
	export let desde;
	export let hasta;
	export let search;

	export let init_slide = 0;
	export let limit_slide = 7;

	/* varriables paginado */
	let url_pag = '';
	let page = 1;
	let offset = 0;

	let num_pages = generatePages();

	/* botones de navegación */
	let deactive = true;
	let deactivenext = false;
	let deactivenav = true;
	let deactivenextnav = false;

	/* variables modal */
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';

	//Variables mimodal 2
	let aDataModalArchivo = {};
	let modalDetalleContentArchivo;
	let mOpenModalGenericoArchivo = false;
	let modalSizeArchivo = '';
	const mToggleModalGenericoArchivo = () =>
		(mOpenModalGenericoArchivo = !mOpenModalGenericoArchivo);

	/* modal */
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	let itemsBreadCrumb = [{ text: 'Proyectos de vinculación', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (eVinculacionPosgrado !== undefined) {
			load = false;
		}else{
			load = false;
		}
	});

	/* load form */
	const toggleModalLoadProyectoVinculacion = async (id = '', ocultar = false) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/alu_vinculacion_posgrado', {
			action: 'load_form_proyecto_vinculacion',
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
				aDataModalArchivo = res.data;
				modalSizeArchivo = 'lg';
				modalDetalleContentArchivo = ComponenteFormProyectoVinculacion;
				mOpenModalGenericoArchivo = !mOpenModalGenericoArchivo;
				modalTitle = 'Agregar proyecto de vinculación';
				if (id) {
					modalTitle = 'Editar proyecto de vinculación';
				}
			}
		}
	};

	/* Ver mas, ver menos Título*/
	function mycollapsemoretitulo(valor, id) {
		//console.log(valor);
		let spancompleted = document.getElementById(`titulo_${id}`);
		let spanvermas = document.getElementById(`spanvermas_titulo_${id}`);
		let spanvermenos = document.getElementById(`spanvermenos_titulo_${id}`);
		if (valor) {
			spancompleted.style.display = '';
			spanvermas.style.display = 'none';
			spanvermenos.style.display = '';
		} else {
			spancompleted.style.display = 'none';
			spanvermas.style.display = '';
			spanvermenos.style.display = 'none';
		}
	};

	/* Ver mas, ver menos */
	function mycollapsemore(valor, id) {
		//console.log(valor);
		let spancompleted = document.getElementById(id);
		let spanvermas = document.getElementById(`spanvermas_${id}`);
		let spanvermenos = document.getElementById(`spanvermenos_${id}`);
		if (valor) {
			spancompleted.style.display = '';
			spanvermas.style.display = 'none';
			spanvermenos.style.display = '';
		} else {
			spancompleted.style.display = 'none';
			spanvermas.style.display = '';
			spanvermenos.style.display = 'none';
		}
	};

	/* Detalle Proyecto Vinculacion */
	const toggleModalDetalleProyectoVinculacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/alu_vinculacion_posgrado', {
			action: 'detalle_proyecto_vinculacion',
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
				aDataModal = res.data;
				modalDetalleContent = ComponenteDetalleProyectoVinculacion;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Detalle de aprobación';
			}
		}
	};

	const actionRun = (event) => {
		mOpenModalGenericoArchivo = false;
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const saveproyectovinculacion = (event) => {
		location.reload();
	};

	/* Buscar */
	const handleSearh = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/alu_vinculacion_posgrado', {
				action: 'list',
				search: search,
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
				eVinculacionPosgrado = res.data['listado'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
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

	const handleSearchReset = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/alu_vinculacion_posgrado', {
				action: 'list'
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
				//console.log(res.data);
				eVinculacionPosgrado = res.data['listado'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
				search = '';
				count = res.data['count'];
				offset = 0;
				page = 1;
			}
			validate_button();
		});
	};


	function generatePages() {
		let num_pages = [];
		let limit_pages = count / limit;
		for (let i = 1; i < limit_pages + 1; i++) {
			num_pages.push(i);
		}
		return num_pages;
	}


	let pagination_function = async (term) => {
		let url_string = 'alumno/alu_vinculacion_posgrado';
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
		url_pag = url_string + '?' + 'action=' + 'list' + '&' + 'limit=' + limit + '&' + 'offset=' + offset;
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
				eVinculacionPosgrado = res.data['listado'];
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
			} else {
				init_slide -= 7;
				limit_slide -= 7;
			}
		} else {
			if (indic == 'next') {
				init_slide += 7;
				limit_slide += 7;
				deactivenav = false;
			} else {
				/* deactivenav = true;
				deactivenextnav = false; */
			}
		}

		if (num_pages.length > limit_slide) {
			deactivenextnav = false;
		} else {
			deactivenextnav = true;
		}
		if (init_slide == 0) {
			deactivenav = true;
		} else {
			deactivenav = false;
		}

		pagination_function(init_slide+1);

	};


	/* Validacion para desactivar botones */
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

	/* delete */
	const eliminarTitulacion = async (vinpos) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `Con esta acción usted eliminará el registro:<br>  <br>
			${vinpos.proyectovinculacion.titulo}. <br> <br>
			<strong>¿Está seguro(a) de eliminar proyecto de vinculación?</strong>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#FE9900',
			confirmButtonText: 'Si, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Eliminando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/alu_vinculacion_posgrado', {
						action: 'delete_proyecto_vinculacion',
						id: vinpos.id
					});
					loading.setLoading(false, 'Eliminando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						goto('/alu_actualizadatos');
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							
							loading.setLoading(false, 'Cargando, espere por favor...');
							location.reload();
						}
					}
				} else {
					addToast({
						type: 'info',
						header: 'Enhorabuena',
						body: 'Has cancelado la acción de eliminar proyecto de vinculación'
					});
				}
			})
			.catch((error) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: error });
			});
	};

</script>

{#if !load}
    {#if !is_error}
        <BreadCrumb
            title="Mis proyectos de vinculación"
            items={itemsBreadCrumb}
            back={backBreadCrumb}
        />

        <div class="row ">
            <div class="container mb-4">
                <a class="btn btn-success btn-sm" on:click={() => toggleModalLoadProyectoVinculacion()}>
                    <i class="bi bi-plus-circle" /> Adicionar Proyecto
                </a>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header ">
                <div class="d-md align-items-center">
                    <div class="row-fluid">
                        <div class="row ">
                            <div class="col-lg-12 col-md-12 col-12  ">
                                <div class="input-group">
                                    <input
                                        class="form-control"
                                        type="text"
                                        id="searchinput "
                                        bind:value={search}
                                        autocomplete="off"
                                        name="search"
                                        placeholder="Buscar por título del proyecto"
										on:keydown={e => e.key === 'Enter' && handleSearh()}
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
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12 col-xm-12 col-md-12">
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table mb-0 table-hover" id="rwd-table-manual">
                                <thead class="table-light">
                                    <tr>
                                        <th
                                            scope="col"
                                            class="border-top-0 text-center align-middle "
                                            style="width: 25rem;">Título</th
                                        >
                                        <th
                                            scope="col"
                                            class="border-top-0 text-center align-middle "
                                            style="width: 50rem;">Descripción</th
                                        >
                                        <th
                                            scope="col"
                                            class="border-top-0 text-center align-middle "
                                            style="width: 10rem;">Estado</th
                                        >
                                        <th
                                            scope="col"
                                            class="border-top-0 text-center align-middle "
                                            style="width: 5rem;">Detalle</th
                                        >
                                        <th
                                            scope="col"
                                            class="border-top-0 text-center align-middle "
                                            style="width: 5rem;">Evidencia</th
                                        >
                                        <th
                                            scope="col"
                                            class="border-top-0 text-center align-middle "
                                            style="width: 5rem;">Acciones</th
                                        >
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each eVinculacionPosgrado as vinpos}
                                        <tr>
                                            <td class="fs-6 align-middle border-top-0 text-justify">
												<span>
                                                    {vinpos.proyectovinculacion.titulo.slice(0, 99)}
												</span>
                                                <span
                                                    id="titulo_{vinpos.proyectovinculacion.id}"
                                                    style="display: none;"
                                                >
                                                    {vinpos.proyectovinculacion.titulo.slice(
                                                        99,
                                                        vinpos.proyectovinculacion.titulo.length
                                                    )}
												</span>

												{#if vinpos.proyectovinculacion.titulo.length > 99}
												<a
													id="spanvermas_titulo_{vinpos.proyectovinculacion.id}"
													href="javascript:void(0)"
													on:click={() => mycollapsemoretitulo(true, vinpos.proyectovinculacion.id)}
													class="badge"
													style="border:1px solid rgba(157, 157, 157, 0.55);
										border-radius:10px;color:black;font-weight: normal;background-color:
										 #fff;cursor:pointer;">...Ver más</a
												>
											{/if}
											<a
												id="spanvermenos_titulo_{vinpos.proyectovinculacion.id}"
												href="javascript:void(0)"
												on:click={() => mycollapsemoretitulo(false, vinpos.proyectovinculacion.id)}
												class="badge"
												style="display: none; border:1px solid rgba(157, 157, 157, 0.55);
										border-radius:10px;color:black;font-weight: normal;background-color:
										 #fff;cursor:pointer;">...Ver menos</a
											>


                                            </td>
                                            <td class="fs-6 border-top-0">
                                                <!-- <span class="truncate-text">{vinpos.proyectovinculacion.descripcion}</span> -->
                                                <span>
                                                    {vinpos.proyectovinculacion.descripcion.slice(0, 150)}
												</span>
                                                <span
                                                    id={vinpos.proyectovinculacion.id}
                                                    style="display: none;"
                                                >
                                                    {vinpos.proyectovinculacion.descripcion.slice(
                                                        150,
                                                        vinpos.proyectovinculacion.descripcion.length
                                                    )}
												</span>

                                                {#if vinpos.proyectovinculacion.descripcion.length > 150}
                                                    <a
                                                        id="spanvermas_{vinpos.proyectovinculacion.id}"
                                                        href="javascript:void(0)"
                                                        on:click={() => mycollapsemore(true, vinpos.proyectovinculacion.id)}
                                                        class="badge"
                                                        style="border:1px solid rgba(157, 157, 157, 0.55);
                                            border-radius:10px;color:black;font-weight: normal;background-color:
                                             #fff;cursor:pointer;">...Ver más</a
                                                    >
                                                {/if}
                                                <a
                                                    id="spanvermenos_{vinpos.proyectovinculacion.id}"
                                                    href="javascript:void(0)"
                                                    on:click={() => mycollapsemore(false, vinpos.proyectovinculacion.id)}
                                                    class="badge"
                                                    style="display: none; border:1px solid rgba(157, 157, 157, 0.55);
													border-radius:10px;color:black;font-weight: normal;background-color:
													#fff;cursor:pointer;">...Ver menos</a
                                                >
												<br />
												{#if vinpos.proyectovinculacion.estadoaprobacion === 1}
												{#if vinpos.proyectovinculacion.detalleaprobacionproyecto }
													<strong >OBSERVACIÓN DOCENTE:</strong>  <br />
													{vinpos.proyectovinculacion.detalleaprobacionproyecto} &#128578;

												{/if}
                                                {/if}

                                            </td>
                                            <td class="fs-8 align-middle border-top-0 text-center">
                                                {#if vinpos.proyectovinculacion.estadoaprobacion === 1}
                                                    <span class="badge bg-success"> APROBADO</span>
                                                {/if}
                                                {#if vinpos.proyectovinculacion.estadoaprobacion === 2}
                                                    <span class="badge bg-secondary"> PENDIENTE</span>
                                                {/if}
                                                {#if vinpos.proyectovinculacion.estadoaprobacion === 3}
                                                    <span class="badge bg-danger"> RECHAZADO</span>
                                                {/if}
                                            </td>
                                            <td class="fs-6 align-middle border-top-0 text-center">
                                                <a
                                                    class="btn btn-info btn-xs"
                                                    on:click|preventDefault={() =>
                                                        toggleModalDetalleProyectoVinculacion(vinpos.id)}
                                                >
                                                    <i class="bi bi-list" />
                                                    <Tooltip target={`tooltip-detail-request${vinpos.id}`} placement="top">
                                                        Ver detalle
                                                    </Tooltip>
                                                </a>
                                            </td>
                                            <td class="fs-6 align-middle border-top-0 text-center">
                                                <a
                                                    class="btn btn-primary btn-xs rounded-pill"
                                                    href={vinpos.download_link}
                                                    target="_blank"
                                                >
                                                    <i class="bi bi-file-pdf" /></a
                                                >
                                            </td>
                                            <td class="fs-6 align-middle border-top-0 text-center">
                                                <div
                                                    style="display:flex;justify-content: center;align-items: center; gap: 5px;"
                                                >
													{#if vinpos.proyectovinculacion.estadoaprobacion !== 1}
														<a class="btn btn-primary btn-xs"
															id={`tooltip-edit-request$1`}
															on:click={() => toggleModalLoadProyectoVinculacion(vinpos.id, true)}
															><i class="bi bi-pencil" />
														</a>
														<Tooltip target={`tooltip-edit-request$1`} placement="top">
															Editar solicitud
														</Tooltip>
														<a class="btn btn-danger btn-xs"
															id={`tooltip-delete-request$2`}
															on:click={() => eliminarTitulacion(vinpos)}
														>
															<i class="bi bi-trash" />
														</a>
														<Tooltip target={`tooltip-delete-request$2`} placement="top">
															Eliminar solicitud
														</Tooltip>
													{/if}
                                                </div>
                                            </td>
                                        </tr>
                                    {:else}
                                        <tr>
                                            <td colspan="8" class="text-center"
                                                >NO EXISTEN MANUAL DE USUARIO EN EL SISTEMA</td
                                            >
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    </div>

					<div class="border-top-0">
						<div class="row mt-3 mb-5 px-3">
							
							<div class="col-lg-12 ">
								<nav>
									<ul class="pagination justify-content-center m-0 ml-4">
										<!-- <li class="page-item">
											<button
												class="page-link btn rounded-pill" hidden
												disabled={deactive}
												on:click|preventDefault={() => pagination_function('prev')}
											>
												<i class="bi bi-chevron-double-left" />
											</button>
										</li> -->
			
											<li class="page-item" >
												<button
													class="page-link btn rounded-pill" hidden={deactivenav}
													disabled={deactivenav}
													on:click|preventDefault={() => collapserdata('prev')}
												>
													<i class="bi bi-chevron" />
													-
												</button>
											</li>
			
											{#each num_pages.slice(init_slide, limit_slide) as num}
												<li class="page-item {num === page ? 'active' : ''}">
													<button
														class="page-link btn rounded-pill"
														on:click|preventDefault={() => pagination_function(num)}
													>
														<i class="bi bi-chevron" />
														{num}
													</button>
												</li>
											{/each}

										{#if count > limit}
											
											<li class="page-item" >
												<button
													class="page-link btn rounded-pill" hidden={deactivenextnav}
													disabled={deactivenextnav}
													on:click|preventDefault={() => collapserdata('next')}
												>
													<i class="bi bi-chevron" />
													+
												</button>
											</li>
											
										{/if}
			
										<!-- <li class="page-item">
											<button
												class="page-link btn  rounded-pill" hidden
												disabled={deactivenext}
												on:click|preventDefault={() => pagination_function('next')}
											>
												<i class="bi bi-chevron-double-right" />
											</button>
										</li> -->
									</ul>
								</nav>
							</div>
			
						</div>
					</div>

                </div>
            </div>
        </div>
    {:else}
        <ModuleError title="Ocurrió un error" message={message_error} />
    {/if}
{:else}
    <div
        class="m-0 vh-100 row justify-content-center align-items-center"
        style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
    >
        <div class="col-auto text-center">
            <Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
            <h3>Verificando la información, espere por favor...</h3>
        </div>
    </div>
{/if}

{#if mOpenModalGenericoArchivo}
	<Modal
		isOpen={mOpenModalGenericoArchivo}
		size={modalSizeArchivo}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader>
			<h4>{modalTitle}</h4>
		</ModalHeader>
		<ModalBody>
			<svelte:component
				this={modalDetalleContentArchivo}
				aData={aDataModalArchivo}
				toggle={mToggleModalGenericoArchivo}
				on:saveproyectovinculacion={saveproyectovinculacion}
			/>
		</ModalBody>
	</Modal>
{/if}

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="lg"
		on:actionRun={actionRun}
	/>
{/if}

<style>
	/* 	CSS variables can be used to control theming.
			https://github.com/rob-balfre/svelte-select/blob/master/docs/theming_variables.md
	*/

	form {
		/*max-width: 400px;*/
		background: #f4f4f4;
		padding: 0;
		border-radius: 4px;
	}

	label {
		margin: 0 0 10px;
	}
	.themed {
		--border: 3px solid blue;
		--borderRadius: 10px;
		--placeholderColor: blue;
	}

</style>
