<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET, loadNotifications } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';
	export const load: Load = async ({ fetch }) => {
		let eNotificaciones = [];
		let next;
		let previous;
		let count;
		let limit;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/notificacion', {});
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
					eNotificaciones = res.data['eNotificaciones'];
					next = res.data['next'];
					previous = res.data['previous'];
					count = res.data['count'];
					limit = res.data['limit'];
				}
			}
		}

		return {
			props: {
				eNotificaciones,
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
	export let eNotificaciones;
	export let next;
	export let previous;
	export let count;
	export let limit;

	export let i_prioridad;

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

	let itemsBreadCrumb = [{ text: 'Mis Notificaciones', active: true, href: undefined }];
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
				console.log('GET ENTER');
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

	const searchNotifi = (e) => {
		//console.log(e);

		const tableRowsInterno = document.querySelectorAll('#rwd-table-notifi tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.nombre_notifi');
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
			loadAjax({}, 'alumno/notificacion', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eNotificaciones = response.value.data['eNotificaciones'];

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

	const VerNotificacion = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'VerNotificacion',
				id: id
			},
			'alumno/notificacion'
		)
			.then(async (response) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (response.value.isSuccess) {
					loadInitial();

					addNotification({
						msg: 'Notificación visualizada.',
						type: 'info'
					});
					await loadNotifications();
				} else {
					addNotification({
						msg: response.value.message,
						type: 'error'
					});
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

	const filterPrioridad = async (i_prioridad) => {
		//console.log('I' + i_prioridad);
		loading.setLoading(true, 'Cargando, espere por favor...');
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiGET(fetch, 'alumno/notificacion', {
				prioridad: i_prioridad
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
				eNotificaciones = res.data['eNotificaciones'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
				offset = 0;
				page = 1;
			}
			validate_data_filtrered();
			validate_button();
		});
	};

	let pagination = async (term) => {
		let url_string = 'alumno/notificacion';
		offset = limit * page;
		/* Pregunta por el boton presionado */
		if (term == 'next') {
			page += 1;
		} else {
			page -= 1;
			offset = limit * page - limit;
		}
		/* Crea la url */
		url_pag =
			url_string + '?' + 'limit=' + limit + '&' + 'offset=' + offset + '&prioridad=' + i_prioridad;
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
				console.log(res.data);
				eNotificaciones = res.data['eNotificaciones'];
				next = res.data['next'];
				previous = res.data['previous'];
				count = res.data['count'];
				limit = res.data['limit'];
			}
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
	function validate_data_filtrered() {
		if (count == '0' || count < 20) {
			deactivenext = true;
			deactive = true;
		} else {
			deactivenext = false;
		}
	}

	// $: {
	// 	//console.log(id_periodo);
	// 	//console.log(id_inscripcion);
	// }
</script>

<svelte:head>
	<title>Mis Notificaciones</title>
</svelte:head>
<BreadCrumb title="Mis Notificaciones" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="row">
	<div class="col-lg-12 col-xm-12 col-md-12">
		<div class="card">
			<div class="card-body">
				<form class="form">
					<div class="row">
						<div class="col-lg-6 col-md-12 col-12">
							<div class="mb-3">
								<label for="selectnotificacion" class="form-label"
									><!-- <i class="bi bi-card-list" /> Prioridad: --></label
								>
								<select
									class="form-control"
									name="selectnotificacion"
									bind:value={i_prioridad}
									on:change={({ target: { value } }) => filterPrioridad(value)}
									id="i_prioridad"
									style="width: 100%"
								>
									<option value="0">TODOS</option>
									<option value="1">
										<span class="badge bg-danger"> ALTA </span>
									</option>
									<option value="2">
										<span class="badge bg-warning"> MEDIA </span>
									</option>
									<option value="3">
										<span class="badge bg-success"> BAJA </span>
									</option>
								</select>
							</div>
						</div>
						<div class="col-lg-6 col-md-12 col-12">
							<div class="mb-3">
								<label for="input" class="form-label"><!-- <i class="bi-search" /> --> </label>
								<input
									type="search"
									class="form-control"
									name="input"
									placeholder="Buscar notificación"
									style="width: 100% !important;"
									on:keyup={({ target: { value } }) => searchNotifi(value)}
								/>
							</div>
						</div>
					</div>
				</form>
				<br />
				<div class="table-responsive">
					<table
						class="table table-striped table-hover table table-sm mb-0 text-nowrap table-border table-hover"
						id="rwd-table-notifi"
					>
						<thead class="table-light">
							<tr>
								<th
									scope="col"
									class="border-top-0 text-center align-middle "
									style="width: 5rem;"
								/>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Prioridad</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Notificación</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>URL</th
								>
							</tr>
						</thead>
						<tbody>
							{#if eNotificaciones.length > 0}
								{#each eNotificaciones as Noti}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-center">
											{#if Noti.leido}
												<i class="bi bi-check-circle" /><br />
												<span class="badge bg-info"> {Noti.fecha_hora_leido} </span>
											{:else}
												<button
													data-bs-toggle="tooltip"
													data-bs-placement="right"
													title="Marcar como leída"
													class="bnt btn-danger rounded-circle"
													on:click={() => VerNotificacion(Noti.id)}
													><svg
														xmlns="http://www.w3.org/2000/svg"
														width="16"
														height="16"
														fill="currentColor"
														class="bi bi-eye-slash-fill"
														viewBox="0 0 16 16"
													>
														<path
															d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7.029 7.029 0 0 0 2.79-.588zM5.21 3.088A7.028 7.028 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.062-2.062a3.5 3.5 0 0 0-4.474-4.474L5.21 3.089z"
														/>
														<path
															d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829l-2.83-2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12-.708.708z"
														/>
													</svg></button
												>
											{/if}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{#if Noti.prioridad == 1}
												<span class="badge bg-danger"> ALTA </span>
											{:else if Noti.prioridad == 2}
												<span class="badge bg-warning"> MEDIA </span>
											{:else if Noti.prioridad == 3}
												<span class="badge bg-success"> BAJA </span>
											{/if}
										</td>
										<td class="fs-6 align-middle border-top-0 text-wrap" style="width: 22rem;">
											<div class="text-center  nombre_notifi">
												<b>{Noti.titulo}</b><br />
												{#if Noti.fecha_hora_visible}
													<span class="badge bg-info">
														<i class="bi bi-eye" /> Disponible hasta {Noti.fecha_hora_visible}
													</span>
												{:else}
													<span class="badge bg-danger">
														<i class="bi bi-eye-slash-fill" /> No visible
													</span>
												{/if}
												<br />{Noti.cuerpo}<br />
											</div>
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{#if Noti.url}
												<a href={Noti.url} target="_blank">
													<svg
														xmlns="http://www.w3.org/2000/svg"
														width="24"
														height="24"
														fill="currentColor"
														class="text-dark"
														viewBox="0 0 16 16"
													>
														<path
															d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1.002 1.002 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4.018 4.018 0 0 1-.128-1.287z"
														/>
														<path
															d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243L6.586 4.672z"
														/>
													</svg>
												</a>
												<!-- <a href="{Noti.url }" class="btn btn-default" target="_self"><i class="bi bi-link-45deg"></i></a> -->
											{:else}
												<span class="badge bg-danger">SIN URL</span>
											{/if}
										</td>
									</tr>{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN NOTIFICACIONES</td>
								</tr>
							{/if}
						</tbody>
					</table>
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
