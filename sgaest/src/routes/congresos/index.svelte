<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eCongresos = [];

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/congreso', {});
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
					eCongresos = res.data['eCongresos'];

				}
			}
		}

		return {
			props: {
				eCongresos,

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
	export let eCongresos;

	let mOpenModalGenerico = false;
	let mOpenConfirmarImportarNotasIngles = false;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
		(mOpenConfirmarImportarNotasIngles = !mOpenConfirmarImportarNotasIngles);

	let itemsBreadCrumb = [{ text: 'Mis congresos', active: true, href: undefined }];
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

	const searchCongreso = (e) => {
		//console.log(e);
		
		const tableRowsInterno = document.querySelectorAll('#rwd-table-congreso tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.nombre_congreso');
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
			loadAjax({}, 'alumno/congreso', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eCongresos = response.value.data['eCongresos'];


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

	
		const confirmarEliminarCongreso = async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Está seguro(a) que desea eliminar su inscripción al congreso: ${nombre}?`,
			type: 'info',
			icon: 'info',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Aceptar',
			cancelButtonText: 'Cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'confirmarEliminarCongreso',
							id: id,
						},
						'alumno/congreso'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								//console.log(response.value.data);
								eCongresos = response.value.data['eCongresos'];

								addNotification({
								msg: 'Se eliminó la inscripción.',
								type: 'info'
								});
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
				} else {
					addNotification({
						msg: 'Se canceló.',
						type: 'warning'
					});
				}
			})
			.catch((error) => {
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};


</script>

<svelte:head>

	<title>Mis congresos</title>
</svelte:head>
<BreadCrumb title="Mis Congresos" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="row">

	<div class="col-lg-12 col-xm-12 col-md-12">
		
		<div class="card">

			<div class="card-body">
				<div class="table-responsive">
					<input
						class="form-control"
						placeholder="Buscar congreso"
						style="width: 100% !important;"
                        on:keyup={({ target: { value } }) => searchCongreso(value)}

					/>
					<table class="table mb-0 table-hover" id="rwd-table-congreso" >
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Congreso</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Tipo de Participación</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Cancelado</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Certificado</th>

							</tr>
						</thead>
						<tbody>
							{#if eCongresos.length > 0}
								{#each eCongresos as congreso}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-center nombre_congreso">
                                            { congreso.congreso.nombre }
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                            { congreso.tipoparticipacion.display }
                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                            {#if congreso.existerubrocurso_2 }
                                                {#if congreso.pagorubrocurso_2 }
                                                <span class="badge bg-success"> SÍ </span>
                                                {:else}
                                                <span class="badge bg-danger"> NO </span>
                                                {/if}
                                            {:else}
                                            <span class="badge bg-warning"> Falta configurar rubro </span>

                                            {/if}
										
                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{#if congreso.existerubrocurso_2 }
                                                {#if congreso.pagorubrocurso_2 }
													{#if congreso.rutapdf}
														{#if congreso.congreso.pk === 20 }
															<a class="btn btn-warning btn-sm" title="Descargar certificación del congreso"
															href="{congreso.rutapdfct}" target="_blank">
																<svg
																xmlns="http://www.w3.org/2000/svg"
																width="24"
																height="24"
																fill="currentColor"
																class="bi bi-file-pdf text-white"
																viewBox="0 0 16 16"
																>

																<path d="M7.5 5.5a.5.5 0 0 0-1 0v.634l-.549-.317a.5.5 0 1 0-.5.866L6 7l-.549.317a.5.5 0 1 0 .5.866l.549-.317V8.5a.5.5 0 1 0 1 0v-.634l.549.317a.5.5 0 1 0 .5-.866L8 7l.549-.317a.5.5 0 1 0-.5-.866l-.549.317V5.5zm-2 4.5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zm0 2a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5z"/>
																<path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>

																
															</a>
														{:else}														
															<a class="btn btn-warning btn-sm" title="Descargar certificación del congreso"
															href="{variables.BASE_API}{congreso.rutapdf}" target="_blank">
																<svg
																	xmlns="http://www.w3.org/2000/svg"
																	width="24"
																	height="24"
																	fill="currentColor"
																	class="bi bi-file-pdf text-white"
																	viewBox="0 0 16 16"
																>
																	<path d="M7.5 5.5a.5.5 0 0 0-1 0v.634l-.549-.317a.5.5 0 1 0-.5.866L6 7l-.549.317a.5.5 0 1 0 .5.866l.549-.317V8.5a.5.5 0 1 0 1 0v-.634l.549.317a.5.5 0 1 0 .5-.866L8 7l.549-.317a.5.5 0 1 0-.5-.866l-.549.317V5.5zm-2 4.5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zm0 2a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5z"/>
																	<path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
																</svg>
															</a>
														{/if}
														
													{/if}
                                                {:else}
																
														<button  data-bs-toggle="tooltip" data-bs-placement="right" title="Eliminar inscripción del congreso"  class="btn btn-danger btn-sm" on:click={() => confirmarEliminarCongreso(congreso.id, congreso.congreso.nombre)}
															><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
																<path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
																<path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
															  </svg></button >
															  
                                                {/if}
                                            {/if}
                                            
										</td>
									
								{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN CONGRESOS</td>
								</tr>
							{/if}
						</tbody>
					</table>
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
