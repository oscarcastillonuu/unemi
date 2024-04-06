<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eSolicitudesFerias = [];
		let eUserLog = 0;
		let eCronogramas = [];
		let enButtonNew = false;
		let habilitar_chatbot;
		let aPersona = {};

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			aPersona = dataSession['persona'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/ferias', {});
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
					eSolicitudesFerias = res.data['eSolicitudesFerias'];
					eUserLog = res.data['eUserLog'];
					eCronogramas = res.data['eCronogramas'];
					enButtonNew = res.data['enButtonNew'];
					habilitar_chatbot = res.data['habilitar_chatbot'];
				}
			}
		}

		return {
			props: {
                eSolicitudesFerias,
				eUserLog,
				eCronogramas,
				enButtonNew,
				habilitar_chatbot,
				aPersona
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
	import ModalGenerico from '$components/Alumno/Feria/ModalSolicitud.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip, Spinner} from 'sveltestrap';
    import Error from '../__error.svelte';
    import ComponenteFormularioSolicitud from './_formsolicitud.svelte';
    let load = true;
    export let eSolicitudesFerias;
    export let eUserLog;
    export let eCronogramas;
    export let enButtonNew;
	export let habilitar_chatbot;
	export let aPersona;
	let itemsBreadCrumb = [{ text: 'FERIA FACI', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
    let aDataModal = {};
	let modalTitle = '';
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});

	const action_init_load = async () => {
		const ds = browserGet('dataSession');
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			aPersona = dataSession['persona'];
			const [res, errors] = await apiGET(fetch, 'alumno/ferias', {});

			//console.log(res);
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					return {
						status: 302,
						redirect: '/'
					};
				} else {
					//console.log(res.data);
					eSolicitudesFerias = res.data['eSolicitudesFerias'];
					eUserLog = res.data['eUserLog'];
					eCronogramas = res.data['eCronogramas'];
					enButtonNew = res.data['enButtonNew'];
					habilitar_chatbot = res.data['habilitar_chatbot'];
				}
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');
	};

	const toggleModalLoadSolicitudFeria = async (id='', ocultar=false) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/ferias', {
			action: 'LoadFormSolicitudFeria',
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
				aDataModal.ocultar = ocultar;
				modalDetalleContent = ComponenteFormularioSolicitud;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Nueva Solicitud';
				if(id && ocultar){
					modalTitle = 'Detalle de Solicitud';
				}else if(id){
					modalTitle = 'Editar Solicitud';
				}
				
			}
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
	const eliminarSolicitudFeria = async (eSolicitudFeria)=>{
			Swal.fire({
                    html: `¿Está seguro de eliminar el registro <span class="badge bg-warning"> ${eSolicitudFeria.display}</span>?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'SI',
                    cancelButtonText: 'NO',
                }).then( async (result) => {
                if (result.isConfirmed) {
					const [res, errors] = await apiPOST(fetch, 'alumno/ferias',{action: 'DeleteSolicitudFeria', id: eSolicitudFeria.id});
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						loading.setLoading(false, 'Cargando, espere por favor...');
						return;
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							if (!res.module_access) {
								goto('/');
							}
							loading.setLoading(false, 'Cargando, espere por favor...');
							return;
						} else {
							addToast({ type: 'success', header: 'Exitoso', body: 'Se elimino correctamente el registro' });							
							loading.setLoading(false, 'Cargando, espere por favor...');
							goto('/alu_ferias');
						}
					}
                }else{
                    addToast({ type: 'success', header: 'Notificación', body: 'Genial salvaste el registro' });
					loading.setLoading(false, 'Cargando, espere por favor...');
					action_init_load();
                }
                }); 
		}
	const actionRun = (event)=>{
		mOpenModalGenerico =false;
		loading.setLoading(false, 'Cargando, espere por favor...');
		action_init_load();
	}
	// const action_generar_actacompromiso = async () => {
	// 	const ds = browserGet('dataSession');
	// 	loading.setLoading(true, 'Cargando, espere por favor...');
	// 	if (ds != null || ds != undefined) {
	// 		const [res, errors] = await apiPOST(fetch, 'alumno/ferias', {action:'generaractacompromiso'});
	//
	// 		//console.log(res);
	// 		if (errors.length > 0) {
	// 			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
	// 			return {
	// 				status: 302,
	// 				redirect: '/'
	// 			};
	// 		} else {
	// 			if (!res.isSuccess) {
	// 				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
	// 				return {
	// 					status: 302,
	// 					redirect: '/'
	// 				};
	// 			} else {
	// 				console.log(res.data);
	// 			}
	// 		}
	// 	}
	// 	loading.setLoading(false, 'Cargando, espere por favor...');
	// };
</script>
<svelte:head>
	<title>FERIA FACI</title>
</svelte:head>
<!-- {#if !load} -->
<BreadCrumb title="FERIA FACI" items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="row">
		<div class="col-12">
			{#each eCronogramas as eCronograma}
			<div class="alert alert-info d-flex align-items-center" role="alert">
			   <svg
				   xmlns="http://www.w3.org/2000/svg"
				   width="24"
				   height="24"
				   fill="currentColor"
				   class="bi bi-info-circle-fill me-2"
				   viewBox="0 0 16 16"
			   >
				   <path
					   d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
				   />
			   </svg>
			   <div>
				   
					   {#if (aPersona.sexo_id == 1)}Estimada {:else }Estimado {/if}<b>{aPersona.nombre_minus}</b>, existe un cronograma  para la feria <b>{eCronograma.display}</b> configurado para su carrera. <br>
					   La fecha de inscripción es desde <b>{eCronograma.fechainicioinscripcion}</b> hasta <b>{eCronograma.fechafininscripcion}</b><br><br>
				   <div style="padding-left: 10px">
					   <b>Nota:</b><br>
					   •  Coordine la participación de su tutor antes de registrar la solicitud.<br>
					   •  La solicitud debe tener un mínimo de  <b>{eCronograma.minparticipantes}</b> participantes y un máximo de <b>{eCronograma.maxparticipantes}</b> participantes.
				   </div>
				
			   </div>
		   </div>
<!--			<div class="alert alert-info d-flex align-items-center" role="alert">-->
<!--			   <svg-->
<!--				   xmlns="http://www.w3.org/2000/svg"-->
<!--				   width="24"-->
<!--				   height="24"-->
<!--				   fill="currentColor"-->
<!--				   class="bi bi-info-circle-fill me-2"-->
<!--				   viewBox="0 0 16 16"-->
<!--			   >-->
<!--				   <path-->
<!--					   d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"-->
<!--				   />-->
<!--			   </svg>-->
<!--			   <div>-->

<!--				   {#if (aPersona.sexo_id == 1)}Estimada {:else }Estimado {/if}<b>{aPersona.nombre_minus}</b>, es importante que no olvide:<br>-->
<!--				   • Hablar con el tutor antes de registrar la solicitud.<br>-->
<!--				   • La solicitud debe tener un mínimo de  <b>{eCronograma.minparticipantes}</b> participantes y un máximo de <b>{eCronograma.maxparticipantes}</b> participantes.-->

<!--			   </div>-->
<!--		   </div>-->


<!--			<div class="alert alert-info d-flex align-items-center" role="alert">-->
<!--			   <svg-->
<!--				   xmlns="http://www.w3.org/2000/svg"-->
<!--				   width="24"-->
<!--				   height="24"-->
<!--				   fill="currentColor"-->
<!--				   class="bi bi-info-circle-fill me-2"-->
<!--				   viewBox="0 0 16 16"-->
<!--			   >-->
<!--				   <path-->
<!--					   d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"-->
<!--				   />-->
<!--			   </svg>-->
<!--			   <div>-->

<!--					   Estimado/a, la solicitud debe tener un mínimo de  <b>{eCronograma.minparticipantes}</b> participantes y un máximo de <b>{eCronograma.maxparticipantes}</b> participantes.-->

<!--			   </div>-->
<!--		   </div>-->
<!--			<div class="alert alert-info d-flex align-items-center" role="alert">-->
<!--			   <svg-->
<!--				   xmlns="http://www.w3.org/2000/svg"-->
<!--				   width="24"-->
<!--				   height="24"-->
<!--				   fill="currentColor"-->
<!--				   class="bi bi-info-circle-fill me-2"-->
<!--				   viewBox="0 0 16 16"-->
<!--			   >-->
<!--				   <path-->
<!--					   d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"-->
<!--				   />-->
<!--			   </svg>-->
<!--			   <div>-->

<!--					   <b>Recuerde</b> hablar con el tutor antes de registrar la solicitud.-->

<!--			   </div>-->
<!--		   </div>-->
		   {:else}
		   <div class="alert alert-warning d-flex align-items-center" role="alert">
			   <svg
				   xmlns="http://www.w3.org/2000/svg"
				   width="24"
				   height="24"
				   fill="currentColor"
				   class="bi bi-info-circle-fill me-2"
				   viewBox="0 0 16 16"
			   >
				   <path
					   d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
				   />
			   </svg>
			   <div>
					{#if (aPersona.sexo_id == 1)}Estimada {:else }Estimado {/if}<b>{aPersona.nombre_minus}</b>, no existe un cronograma  de feria configurado para su carrera.
			   </div>
		   </div>
			{/each}
		</div>
	</div>
	<div class="row">
		<!--{#if enButtonNew }-->
			<div class="container mb-4">
				<a class="btn btn-success btn-sm" on:click={() => toggleModalLoadSolicitudFeria()} > 
					<i class="bi bi-file-earmark-plus-fill"></i> Adicionar  Solicitud
				</a>
			</div>
		<!--{/if}-->

		<div class="col-12">
			<div class="card mb-4">
				<!-- Card header -->
				<div class="card-header">
					<h4 class="mb-0 display-6 text-center">
						Listado  de solicitudes para presentar proyectos
					</h4>
				</div>
				<!-- Card body -->
				<div class="card-body">
					<div class="table-responsive">
						<!--border-0 table-invoice-->
						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>TITULO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>RESUMEN</th>

                                    <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                        >PARTICIPANTES</th>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                        >PRESENTACIÓN PROPUESTA</th>
                                    <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                        >ESTADO</th>

									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										></th
									>
								</tr>
							</thead>
							<tbody>
								{#if eSolicitudesFerias.length > 0}
									{#each eSolicitudesFerias as eSolicitudFeria}
										<tr>
											<td class="text-wrap fs-6">
												{eSolicitudFeria.titulo}<br>
												<b>Tutor:</b> <span class="avatar avatar-sm"><img src="{eSolicitudFeria.tutor.persona.foto_perfil}" class="rounded-circle"></span>{eSolicitudFeria.tutor.persona.display} <br>
												<span class="badge bg-info">{eSolicitudFeria.cronograma.display}</span>
											</td>
											<td class="text-wrap fs-6" style="text-align: center;">
												<div class="accordion" id="accordionResumen{eSolicitudFeria.id}">
													<div class="accordion-item">
													  <h2 class="accordion-header" id="headingOneResumen{eSolicitudFeria.id}">
														<button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOneResumen{eSolicitudFeria.id}" aria-expanded="true" aria-controls="collapseOneResumen{eSolicitudFeria.id}">
														  Resumen
														</button>
													  </h2>
													  <div id="collapseOneResumen{eSolicitudFeria.id}" class="accordion-collapse collapse" aria-labelledby="headingOneResumen{eSolicitudFeria.id}" data-bs-parent="#accordionResumen{eSolicitudFeria.id}">
														<div class="accordion-body">
															<p class="text-wrap p-0 m-0">{eSolicitudFeria.resumen}</p>
														</div>
													  </div>
													</div>
												</div>  
											</td>
											<td class="fs-6" style="text-align: center; padding-left: 0.9rem;">
												<div style="height: 3rem; width: 3rem;">
													{#each eSolicitudFeria.participantes as participante, index}
														{#if index< 3}
															<span class="avatar avatar-sm">
																<img src="{participante.foto}" class="rounded-circle">
															</span>
														{/if}
													{/each}
													{#if eSolicitudFeria.participantes.length > 3}
													 <span class="avatar avatar-sm avatar-primary">
														<span class="avatar-initials rounded-circle fs-6">
															+{eSolicitudFeria.participantes.length - 3}
														</span>
													  </span>
													{/if}
												  </div>
											</td>
											<td class="fs-6" style="text-align: center">
												<a class="btn btn-info btn-sm"
												       target="_blank"
													   id="{`tooltip-ver-request${eSolicitudFeria.id}`}"
													   href="{eSolicitudFeria.docpropuesta}">
														<i class="bi bi-file-arrow-down-fill"></i>
													</a>
													<Tooltip target={`tooltip-ver-request${eSolicitudFeria.id}`}
															 placement="top">
														Ver Presentación Propuesta
													</Tooltip>
											</td>
											<td class="fs-6" style="text-align: center;">
                                                {#if eSolicitudFeria.estado == 1}
                                                    <span class="badge bg-warning">SOLICITADO</span>
                                                {:else if  eSolicitudFeria.estado == 2}
                                                    <span class="badge bg-success">APROBADO</span>
                                                {:else if eSolicitudFeria.estado == 3}
                                                    <span class="badge bg-danger">RECHAZADO</span>
                                                {/if}
											</td>

											<td class="fs-6" style="text-align: center;">
												{#if eSolicitudFeria.usuario_creacion == eUserLog  && eSolicitudFeria.estado != 3 && eSolicitudFeria.modificarsolicitud }
													<a class="btn btn-primary btn-sm"
													   id="{`tooltip-edit-request${eSolicitudFeria.id}`}"
													   on:click={() => toggleModalLoadSolicitudFeria(eSolicitudFeria.id)} >
														<i class="bi bi-pencil"></i>
													</a>
													<Tooltip target={`tooltip-edit-request${eSolicitudFeria.id}`}
															 placement="top">
														Editar solicitud
													</Tooltip>
												{/if}
												<a class="btn btn-info btn-sm"
												   id="{`tooltip-detail-request${eSolicitudFeria.id}`}"
												   on:click={() => toggleModalLoadSolicitudFeria(eSolicitudFeria.id, true)} >
													<i class="bi bi-info-circle-fill"></i>
													<Tooltip target={`tooltip-detail-request${eSolicitudFeria.id}`}
															 placement="top">
														Ver detalle
													</Tooltip>
												</a>

												{#if eSolicitudFeria.usuario_creacion == eUserLog  &&  eSolicitudFeria.estado == 1}
													<a class="btn btn-danger btn-sm"
													   id="{`tooltip-delete-request${eSolicitudFeria.id}`}"
													   on:click={() => eliminarSolicitudFeria(eSolicitudFeria)} >
														<i class="bi bi-trash"></i>
													</a>
													<Tooltip target={`tooltip-delete-request${eSolicitudFeria.id}`}
															 placement="top">
														Eliminar solicitud
													</Tooltip>
												{/if}
												{#if eSolicitudFeria.certificado_participacion && eSolicitudFeria.estado == 2}
													<a class="btn btn-success btn-sm"
													   target="_blank"
													   id="{`tooltip-certificate-participant${eSolicitudFeria.id}`}"
													   href="{eSolicitudFeria.certificado_participacion}">
														<i class="bi bi-download"></i>
													</a>
													<Tooltip target={`tooltip-certificate-participant${eSolicitudFeria.id}`}
															 placement="top">
														Certificado de participación
													</Tooltip>
												{/if}
												{#if eSolicitudFeria.certificado_ganador && eSolicitudFeria.es_ganador}
													<a class="btn btn-warning btn-sm"
													   target="_blank"
													   id="{`tooltip-certificate-winner${eSolicitudFeria.id}`}"
													   href="{eSolicitudFeria.certificado_ganador}">
														<i class="bi bi-trophy-fill"></i><i class="bi bi-download"></i>
													</a>
													<Tooltip target={`tooltip-certificate-winner${eSolicitudFeria.id}`}
															 placement="top">
														Certificado de ganador carrera
													</Tooltip>
												{/if}
                                                {#if eSolicitudFeria.certificado_ganadorfacultad && eSolicitudFeria.es_ganadorfacultad == '2'}
													<a class="btn btn-warning btn-sm"
													   target="_blank"
													   id="{`tooltip-certificate-winner-faculty${eSolicitudFeria.id}`}"
													   href="{eSolicitudFeria.certificado_ganadorfacultad}">
														<i class="bi bi-trophy-fill"></i><i class="bi bi-upload"></i>
													</a>
													<Tooltip target={`tooltip-certificate-winner-faculty${eSolicitudFeria.id}`}
															 placement="top">
														Certificado de ganador facultad
													</Tooltip>
												{/if}
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="8" class="text-center"
											>NO EXISTEN SOLICITUDES DISPONIBLES</td
										>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
<!-- {:else}
	<div
		class="mt-4 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if} -->
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
		on:actionRun={actionRun}
	/>
{/if}
{#if habilitar_chatbot}
	<script lang="js">
		(function(a,m,o,c,r,m){
			a[m]={
				id:"408120",
				hash:"851af31126ff3352c5f9a6506131e20b07cef6578478fab52d1dc4c5b1781e3e",
				locale:"es",
				inline:false,
				setMeta:function(p){
					this.params=(this.params||[]).concat([p])
				}
				};
			a[o]=a[o]||function(){
				(a[o].q=a[o].q||[]).push(arguments)
			};
			var d=a.document,
			s=d.createElement('script');
			s.async=true;
			s.id=m+'_script';
			s.src='https://amo.to/H/RJ3XM7/CZJLFV'
		}(window,0,"amoSocialButton",0,0,"amo_social_button"));
	</script>
{/if}