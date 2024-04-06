<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eOfertas = [];
		let idinscrip=0;


		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/oferta_laboral', {});
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
					// console.log(res.data);
					eOfertas = res.data['eOfertas'];
					idinscrip = res.data['idinscrip'];

				}
			}
		}

		return {
			props: {
				eOfertas,
				idinscrip

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
	import ComponenteGuia from './_detalle.svelte';

	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
import Error from '../__error.svelte';
import Automatricula from '../alu_matricula/_Pregrado/_automatricula.svelte';
	export let eOfertas;
	export let idinscrip;
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenConfirmarImportarNotasIngles = false;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
		(mOpenConfirmarImportarNotasIngles = !mOpenConfirmarImportarNotasIngles);

	let itemsBreadCrumb = [{ text: 'Ofertas laborales', active: true, href: undefined }];
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

	const searchVacante = (e) => {
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
			loadAjax({}, 'alumno/oferta_laboral', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eOfertas = response.value.data['eOfertas'];


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

	const toggleModalDetalleOferta = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/oferta_laboral', {
			action: 'detalleOferta',
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
				modalDetalleContent = ComponenteGuia;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Detalle Oferta Laboral';
			}
		}
	};

	const confirmarAplicar = async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Está seguro(a) que desea Solicitar Oferta Laboral: ${nombre} Favor después de confirmar actualizar su Hoja de Vida`,
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
							action: 'confirmarAplicar',
							id: id,
							idins: idinscrip
						},
						'alumno/oferta_laboral'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {

								loadInitial()

								addNotification({
								msg: 'Se aplicó a la vacante.',
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

	const confirmarCita= async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Está seguro(a) que desea Solicitar Oferta Laboral: ${nombre} Favor después de confirmar actualizar su Hoja de Vida`,
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
							action: 'confirmarAplicar',
							id: id,
							idins: idinscrip
						},
						'alumno/oferta_laboral'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {

								loadInitial()

								addNotification({
								msg: 'Se aplicó a la vacante.',
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

	const EliminarPostulacion = async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Esta seguro(a) que desea eliminar: ${nombre}?`,
			type: 'info',
			icon: 'error',
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
							action: 'deletefertalaboral',
							id: id
						},
						'alumno/oferta_laboral'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {

								loadInitial()

								addNotification({
								msg: 'Se eliminó vacante.',
								type: 'error'
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
	const confirmarAplicarEstado = async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Está seguro(a) que desea Solicitar Oferta Laboral: ${nombre} Favor después de confirmar actualizar su Hoja de Vida`,
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
							action: 'registarestado',
							id: id,
							idins: idinscrip
						},
						'alumno/oferta_laboral'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {

								loadInitial()

								addNotification({
								msg: 'Se aplicó a la vacante.',
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

	<title>Ofertas laborales</title>
</svelte:head>
<BreadCrumb title="Ofertas laborales" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="row">

	<div class="col-lg-12 col-xm-12 col-md-12">
		
		<div class="card">

			<div class="card-body">
				<div class="table-responsive">
					<input
						class="form-control"
						placeholder="Buscar oferta laboral"
						style="width: 100% !important;"
                        on:keyup={({ target: { value } }) => searchVacante(value)}

					/>
					<table class="table mb-0 table-hover" id="rwd-table-congreso" >
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Área / Cargo</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Lugar/Hora/Fecha/Contacto</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Salario</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Inicio</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Fin</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Abierta</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Vacantes</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Detalles</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Observaciones</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Acciones</th>

							</tr>
						</thead>
						<tbody>
							{#if eOfertas.length > 0}
								{#each eOfertas as oferta}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-center nombre_congreso">
                                            <b>{oferta.area.display }</b><br>{ oferta.cargo }
                                            {#if oferta.graduado }<br>
                                             <b> Requiere Título:</b> <span class="badge bg-warning">SI</span>
                                            {/if}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                            {#if oferta.esta_registrado &&  oferta.esta_registrado.horaentrevista }
                                                {oferta.esta_registrado.lugar} <br> {oferta.esta_registrado.fechaentrevista}, {oferta.esta_registrado.horaentrevista}<br>
                                                {oferta.esta_registrado.personacontacto} <br> {oferta.esta_registrado.telefonocontacto}
                                                {#if oferta.esta_registrado.confirmar_cita }
                                                    <br> <button  data-bs-toggle="tooltip" data-bs-placement="right" title="Aplicar Vacante"  class="btn btn-success btn-sm" on:click={() => confirmarCita(oferta.esta_registrado.id, oferta.cargo)}
														><i class="bi bi-calendar2-check"></i> Confirmar Cita</button >
                                                {:else}
                                                <br> <span class="badge bg-info">Cita confirmada</span>

                                                {/if}
                                            {/if}

                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                    		{oferta.salario}
                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center">
											{oferta.inicio}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{oferta.fin}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{#if !oferta.esta_cerrada}
                                            <span class="badge bg-success" title="SI"> <i class="bi bi-check-circle-fill"></i> </span>

                                            {/if}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{oferta.plazas}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
                                            <a class="btn btn-warning btn-sm"  on:click={() => toggleModalDetalleOferta(oferta.id)}>

                                                <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                width="24"
                                                height="24"
                                                fill="currentColor"
                                                class="bi bi-file-pdf text-white"
                                                viewBox="0 0 16 16"
                                            >

                                            <path d="M2 3.5a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5zm.646 2.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1 0 .708l-2 2a.5.5 0 0 1-.708-.708L4.293 8 2.646 6.354a.5.5 0 0 1 0-.708zM7 6.5a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5zm-5 3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5z"/>

                                            </svg>
										</a>
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{#if oferta.observaciones }
												{#each oferta.observaciones as ob, i}
												{i+1} {ob.observacion} <br>
												{/each}
											{/if}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{#if !oferta.esta_cerrada}
                                            	{#if !oferta.esta_registrado}
												<button  data-bs-toggle="tooltip" data-bs-placement="right" title="Aplicar Vacante"  class="btn btn-success btn-sm" on:click={() => confirmarAplicar(oferta.id, oferta.cargo)}
													><i class="bi bi-calendar2-check"></i> Aplicar</button >

												{:else}
													{#if oferta.esta_registrado.estado }
														{#if !oferta.esta_registrado.valida}
														<button  data-bs-toggle="tooltip" data-bs-placement="right" title="Eliminar Vacante"  class="btn btn-danger btn-sm" on:click={() => EliminarPostulacion(oferta.esta_registrado.id, oferta.cargo)}
															><i class="bi bi-trash-fill"></i> Eliminar</button >

														{/if}
													{:else}
													<button  data-bs-toggle="tooltip" data-bs-placement="right" title="Aplicar Vacante"  class="btn btn-success btn-sm" on:click={() => confirmarAplicarEstado(oferta.esta_registrado.id, oferta.cargo)}
														><i class="bi bi-calendar2-check"></i> Aplicar</button >

													{/if}

												{/if}


                                            {/if}
										</td>
                                        


									
									
								{/each}
							{:else}
								<tr>
									<td colspan="10" class="text-center">NO EXISTEN OFERTAS LABORALES</td>
								</tr>
							{/if}
						</tbody>
					</table>
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
