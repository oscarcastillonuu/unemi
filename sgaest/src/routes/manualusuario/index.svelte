<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eManualesUsuario = [];
		let next;
		let previous;
		let count;
		let limit;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/manual_usuario', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
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
					eManualesUsuario = res.data['eManualesUsuario'];
					next = res.data['next'];
					previous = res.data['previous'];
					count = res.data['count'];
					limit = res.data['limit'];
				}
			}
		}
		return {
			props: {
				eManualesUsuario,
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
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
	import Error from '../__error.svelte';

	/* Data exportada */
	export let eManualesUsuario;
	export let next;
	export let previous;
	export let count;
	export let limit;

	/* variables para filtro */
	export let desde;
	export let hasta;
	export let search;

	/* varriables paginado */
	let url_pag = '';
	let page = 1;
	let offset = 0;

	/* botones de navegación */
	let deactive = true;
	let deactivenext = false;

	let mOpenModalGenerico = false;
	let mOpenConfirmarImportarNotasIngles = false;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	mOpenConfirmarImportarNotasIngles = !mOpenConfirmarImportarNotasIngles;

	let itemsBreadCrumb = [{ text: 'Manuales de usuarios', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});

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

	const searchManual = (e) => {
		//console.log(e);

		const tableRowsInterno = document.querySelectorAll('#rwd-table-manual tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.nombre_manual');
			if (
				converToAscii(nombre_interno.innerText.toLowerCase()).indexOf(
					converToAscii(e.toLowerCase())
				) === -1
			) {
				rowInterno.style.display = 'none';
			} else {
				rowInterno.style.display = '';
			}
		}
	};

	const loadInitial = () =>
		new Promise((resolve, reject) => {
			loadAjax({}, 'alumno/manual_usuario', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eManualesUsuario = response.value.data['eManualesUsuario'];
						resolve({
							error: false,
							value: true
						});
					} else {
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
					reject({
						error: true,
						message: error.message
					});
				});
		});

	/* Buscar por nombre y por fecha */


	const handleSearh = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/manual_usuario', {
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
				console.log(res);
				eManualesUsuario = res.data['eManualesUsuario'];
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

	const handleSearchReset = () =>{
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/manual_usuario', {});
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
				eManualesUsuario = res.data['eManualesUsuario'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];				
				search = res.data['search'];				
				count = res.data['count'];
				desde = '';
				hasta = '';
				offset = 0;
				page = 1;
			}		
			validate_button();	
		});		
	};

	let pagination = async (term) => {
		let url_string = 'alumno/manual_usuario';
		offset = limit * page;
		/* Pregunta por el boton presionado */
		if (term == 'next') {
			page += 1;
		} else {
			page -= 1;
			offset = limit * page - limit;
		}
		/* Crea la url */
		url_pag = url_string + '?' + 'limit=' + limit + '&' + 'offset=' + offset;
		//console.log(url_pag);
		/* Realiza consulta a la base */
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
				//console.log(res.data);
				eManualesUsuario = res.data['eManualesUsuario'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
			}
			/* Validacion para desactivar botones */
			validate_button();
		});
		
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
</script>

<svelte:head>
	<title>Manuales de Usuarios</title>
</svelte:head>
<BreadCrumb title="Manuales de Usuarios" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="card mb-4">
	<div class="card-header border-bottom-1">
		<div class="d-md align-items-center">
			<div class="row-fluid">
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
								><i class="bi bi-people " title="Estudiante" /> Manual de Usuario:</label
							>
							<div class="input-group">
								<input
									class="form-control"
									type="text"
									id="searchinput "
									bind:value={search}
									autocomplete="off"
									name="search"
									placeholder="Buscar manual de usuaio"
								/>
								<button
									class="btn btn-outline-primary"
									type="button"
									on:click|preventDefault={handleSearh}><i class="bi-search rounded-pill" /></button
								>
								<button
									class="btn btn-outline-warning"
									type="button"
									id="btnWarning"
									on:click|preventDefault={handleSearchReset}><i class="bi bi-arrow-repeat " /></button
								>
							</div>
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
					<!-- <input
						class="form-control"
						placeholder="Buscar manual de usuario"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchManual(value)}
						on:keyup={({ target: { value } }) => searchManual(value)}
						on:keyup={({ target: { value } }) => searchManual(value)}
					/> -->
					

					<table class="table mb-0 table-hover" id="rwd-table-manual">
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 45rem;"
									>Nombre</th
								>
								<th scope="col" class="border-top-0 text-center align-middle ">Versión</th>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Fecha</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Archivo</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Observación</th
								>
							</tr>
						</thead>
						<tbody>
							{#if eManualesUsuario}
								{#each eManualesUsuario as manual}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-center nombre_manual">
											{manual.nombre}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{manual.version}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{manual.fecha}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{#if manual.archivo}
												<a href={manual.download_link} target="_blank">
													<svg
														xmlns="http://www.w3.org/2000/svg"
														width="24"
														height="24"
														fill="currentColor"
														class="bi bi-file-pdf text-success"
														viewBox="0 0 16 16"
													>
														<path
															fill-rule="evenodd"
															d="M14 4.5V14a2 2 0 0 1-2 2h-1v-1h1a1 1 0 0 0 1-1V4.5h-2A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v9H2V2a2 2 0 0 1 2-2h5.5L14 4.5ZM1.6 11.85H0v3.999h.791v-1.342h.803c.287 0 .531-.057.732-.173.203-.117.358-.275.463-.474a1.42 1.42 0 0 0 .161-.677c0-.25-.053-.476-.158-.677a1.176 1.176 0 0 0-.46-.477c-.2-.12-.443-.179-.732-.179Zm.545 1.333a.795.795 0 0 1-.085.38.574.574 0 0 1-.238.241.794.794 0 0 1-.375.082H.788V12.48h.66c.218 0 .389.06.512.181.123.122.185.296.185.522Zm1.217-1.333v3.999h1.46c.401 0 .734-.08.998-.237a1.45 1.45 0 0 0 .595-.689c.13-.3.196-.662.196-1.084 0-.42-.065-.778-.196-1.075a1.426 1.426 0 0 0-.589-.68c-.264-.156-.599-.234-1.005-.234H3.362Zm.791.645h.563c.248 0 .45.05.609.152a.89.89 0 0 1 .354.454c.079.201.118.452.118.753a2.3 2.3 0 0 1-.068.592 1.14 1.14 0 0 1-.196.422.8.8 0 0 1-.334.252 1.298 1.298 0 0 1-.483.082h-.563v-2.707Zm3.743 1.763v1.591h-.79V11.85h2.548v.653H7.896v1.117h1.606v.638H7.896Z"
														/>
													</svg>
												</a>
											{/if}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{manual.observacion}
											{manual.observacion}

											{manual.observacion}
										</td>
									</tr>{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN MANUAL DE USUARIO EN EL SISTEMA</td
									>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
			<div class="border-top-0">
				<div class="row my-3 px-3">
					<div class="col-lg-12 gridjs-pagination">
						<nav>
							<ul class="pagination justify-content-center m-0">
								<li class="page-item">
									<button
										class="page-link btn rounded-pill"
										disabled={deactive}
										on:click|preventDefault={() => pagination('prev')}
									>
										<i class="bi bi-chevron-double-left" />
									</button>
								</li>
								<li class="page-item">
									<button
										class="page-link btn  rounded-pill"
										disabled={deactivenext}
										on:click|preventDefault={() => pagination('next')}
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
</div>

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
