<script context="module" lang="ts">
	import { browserGet,apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';

	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eActividades = [];
		let ePreInscripcionens = [];
		let idinscrip = 0;
		let inscripcion = [];
		let totalinscritosalu = 0;
		let maximo_actextracurricular = 0;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/complementarias', {});
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
					console.log(res.data);
					inscripcion = res.data['eInscripcion'];
					eActividades = res.data['eActividadesComple'];
					ePreInscripcionens = res.data['ePreInscripciones'];
					totalinscritosalu = res.data['totalinscritosalu'];
					maximo_actextracurricular = res.data['maximo_actextracurricular'];

				}
			}
		}

		return {
			props: {
				eActividades,
				ePreInscripcionens,
				inscripcion,
				totalinscritosalu,
				maximo_actextracurricular
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
	import { Badge, Spinner } from 'sveltestrap';
	import { loading } from '$lib/store/loadingStore';
	import ComponenteGuia from './_solicitudeliminacion.svelte';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { createEventDispatcher, onDestroy } from 'svelte';

    const dispatch = createEventDispatcher();

	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
	import Error from '../__error.svelte';
	export let eActividades;
	export let ePreInscripcionens;
	export let inscripcion;
	export let totalinscritosalu;
	export let maximo_actextracurricular;

	let nombrecabecera = '';
	
	let eIdELiminar = '';
	let eIdInscripcion = '';

	let mSizeEliminacionSolicitud = 'lg';
	let mOpenEliminacionSolicitud = false;
	const mToggleEliminacionSolicitud = () => (mOpenEliminacionSolicitud = !mOpenEliminacionSolicitud);
    let observacion;

	let mSizeArchivoInscripcion = 'lg';
	let mOpenArchivoInscripcion = false;
	const mToggleArchivoInscripcion = () => (mOpenArchivoInscripcion = !mOpenArchivoInscripcion);

	let mOpenModalGenerico = false;
	let modalDetalleContent;
	let modalTitle = '';
	let aDataModal = {};
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let load = true;

	let pondDocumento;
	let nameDocumento = 'fileDocumento';
	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	let itemsBreadCrumb = [
		{ text: 'Mis Actividades Complementarias', active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (inscripcion){
			load = false;
		}
		console.log(load);
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
			loadAjax({}, 'alumno/complementarias', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						inscripcion = response.value.data['eInscripcion'];
						eActividades = response.value.data['eActividadesComple'];
						ePreInscripcionens = response.value.data['ePreInscripciones'];
						totalinscritosalu = response.value.data['totalinscritosalu'];
						maximo_actextracurricular = response.value.data['maximo_actextracurricular'];

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

	const confirmarInscripcion= async (id, nombre) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `¿Esta seguro(a) que se desea inscribir en la actividad: ${nombre}?`,
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
							action: 'addinscripcion',
							id: id,
						},
						'alumno/complementarias'
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
	const handleAddFile = (err, fileItem) => {
		console.log(pondDocumento.getFiles());
		console.log('A file has been added', fileItem);
	};

	const closeConfirmarMatricula = () => {
		mOpenEliminacionSolicitud = false;
	};
	const closeArchivoInscripcion = () => {
		mOpenArchivoInscripcion = false;
	};
	const openEliminacionSolicitud = (nombre, id) => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		mSizeEliminacionSolicitud = 'lg';
		mOpenEliminacionSolicitud = true;
		nombrecabecera = nombre;
		eIdELiminar = id;
	};
	const openArchivoInscripcion = (nombre, id) => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		mSizeArchivoInscripcion = 'lg';
		mOpenArchivoInscripcion = true;
		eIdInscripcion = id;
		nombrecabecera = nombre;

	};

	const saveInfoPersonal = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoPersonal = document.querySelector('#frmInfoPersonal');
		const formData = new FormData($frmInfoPersonal);
		formData.append('action', 'solicitudeliminacion');

		if (!eIdELiminar) {
            addNotification({
                msg: 'No se encuentra inscripción a eliminar.',
                type: 'error',
                target: 'newNotificationToast'
            });
            loading.setLoading(false, 'Cargando, espere por favor...');
            return;
        }

		formData.append('idEliminar', eIdELiminar);

        if (!observacion) {
            addNotification({
                msg: 'Favor complete el campo de observación',
                type: 'error',
                target: 'newNotificationToast'
            });
            loading.setLoading(false, 'Cargando, espere por favor...');
            return;
        }
    
        formData.append('observacion', observacion);
		
		
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/complementarias', formData);

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
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenEliminacionSolicitud = false;
				loadInitial()
				observacion = '';

			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveInfoArchivo = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoArchivo = document.querySelector('#frmInfoArchivo');
		const formData = new FormData($frmInfoArchivo);

		formData.append('action', 'archivoinscripcion');
		if (!eIdInscripcion) {
            addNotification({
                msg: 'No se encuentra inscripción a eliminar.',
                type: 'error',
                target: 'newNotificationToast'
            });
            loading.setLoading(false, 'Cargando, espere por favor...');
            return;
        }

		formData.append('id', eIdInscripcion);

		let fileDocumento = pondDocumento.getFiles();
		if (fileDocumento.length == 0) {
			addNotification({
				msg: 'Debe subir archivo de documento de inscripción',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileDocumento.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileDocumento = undefined;
		if (pondDocumento && pondDocumento.getFiles().length > 0) {
			eFileDocumento = pondDocumento.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumento', eFileDocumento.file);

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/complementarias', formData);

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
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenArchivoInscripcion = false;
				loadInitial()
				observacion = '';

			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

</script>

<svelte:head>
	<title>Mis Actividades Complementarias</title>
</svelte:head>
{#if !load}
<BreadCrumb title="Mis Actividades Complementarias" items={itemsBreadCrumb} back={backBreadCrumb} />
<div class="row">
	<div class="col-lg-12 col-xm-12 col-md-12">
		<div class="card">
            <div class="card-header text-center">
				<h4 class="mb-0 display-6">Mis Actividades</h4>
			</div>
			<div class="card-body">
				<div class="table-responsive">
					<input
						class="form-control"
						placeholder="Buscar actividad"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCongreso(value)}
					/>
					<table class="table mb-0 table-hover" id="rwd-table-congreso">
						<thead class="table-light">
							<tr>
								<th   style="width: 15px">Nº</th>

								<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;"
									>Área</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Actividad / Facultad</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 35rem;"
									>Detalle</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " 
									>Calificación</th
								>
								<th scope="col" class="border-top-0 text-center align-middle "
									>Fecha inicio / Fin inscripción</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " 
									>Fecha inscripción</th
								>
								
								<th scope="col" class="border-top-0 text-center align-middle " 
									>Acción</th
								>
							</tr>
						</thead>
						<tbody>
							{#if ePreInscripcionens.length > 0}
								{#each ePreInscripcionens as inscrito, i}
									<tr>
										<td  style="width: 15px">
											{i+1}
										</td>

										<td class="fs-6 align-middle border-top-0 text-center">
												<img src="https://sga.unemi.edu.ec/static/images/iconos/actividades/{ inscrito.actividades.periodoarea.areas.colorfondo }"> <strong>{inscrito.actividades.periodoarea.areas.nombre}</strong> 
										</td>

                                        <td class="fs-6 align-middle border-top-0 ">

											{inscrito.actividades.nombre} <br>
											{inscrito.actividades.coordinacion.display} <br>
											{inscrito.matricula.nivel.periodo.display} <br>
											{#if inscrito.actividades.general}
											<span class="badge bg-info"> INDUCCIÓN GENERAL </span> <br>
											{/if}
											{#if !inscrito.en_uso}
												{#if inscrito.puedeenviarsolicitudalumno}
													<span class="badge bg-warning">Puede enviar solicitud de eliminación</span>
												{:else if inscrito.enviosolicitud }
													<b> Observación: </b>{inscrito.enviosolicitud.observacion }<br>
													<b> Estado solicitud eliminación: </b>
													{#if inscrito.enviosolicitud.estado == 1}
													<span class="badge bg-warning"> {inscrito.enviosolicitud.estado_display } </span>

													{/if}
													{#if inscrito.enviosolicitud.estado == 2}
													<span class="badge bg-success"> {inscrito.enviosolicitud.estado_display } </span>

													{/if}
													{#if inscrito.enviosolicitud.estado == 3}
													<span class="badge bg-danger"> {inscrito.enviosolicitud.estado_display } </span>

													{/if}

												{:else}
												<span class="badge bg-danger"> No puede enviar solicitud de eliminación </span>

												{/if}
											{/if}
											{#if inscrito.actividades.calificar } 
											<span class="badge bg-primary"> ACTIVIDAD CON CALIFICACIÓN </span>
											{:else}
											<span class="badge bg-secondary"> ACTIVIDAD SIN CALIFICACIÓN </span>

											{/if}
                                            <br/><b>{ inscrito.actividades.grupo_display }</b>

										</td>
                                        <td class="fs-6 text-justify">
                                            {inscrito.actividades.descripcion}
                                            {#if inscrito.actividades.link}
												<br>												
												<a class="btn btn-info btn-sm" on:click={() => openArchivoInscripcion(inscrito.actividades.display, inscrito.id)} > <i class="bi bi-folder-symlink-fill"></i> Enviar documento de Inscripción</a><br>

												{#if inscrito.archivo}
												<a class="btn btn-info btn-sm tu" title="Descargar código QR" target="_blank" href="{ inscrito.download_link }" ><i class="bi bi-qr-code-scan"></i></a>
												{/if}
                                                <br>
                                                <b>link del evento: </b><a target="_blank" href="{ inscrito.actividades.link }" >{ inscrito.actividades.link }</a>
                                            {/if}
                                            
                                            {#if inscrito.actividades.listafechas.length > 0 }
                                            <div class="accordion accordion-flush" id="accordionDocumentos">
                                                <div class="accordion-item" >
                                                    <h2
                                                        class="accordion-header" 
                                                        id="flush-heading-{inscrito.actividades.idm}"
                                                    >
                                                        <button
                                                            class="accordion-button collapsed " style="height: 45px;"
                                                            type="button"
                                                            data-bs-toggle="collapse"
                                                            data-bs-target="#flush-collapse-{inscrito.actividades.idm}"
                                                            aria-expanded="true"
                                                            aria-controls="flush-collapse-{inscrito.actividades.idm}"
                                                        >
                                                        <h5>Horarios <i class="bi bi-calendar-range-fill" style="color:green"></i></h5> 
                                                        </button
                                                        >
                                                    </h2>
                                                    <div
                                                        id="flush-collapse-{inscrito.actividades.idm}"
                                                        class="accordion-collapse collapse"
                                                        aria-labelledby="flush-heading-{inscrito.actividades.idm}"
                                                        data-bs-parent="#accordionDocumentos"
                                                    >
                                                        {#each inscrito.actividades.listafechas as lista}
                                                            <!-- <div class="accordion-body" style="text-align: left"> -->
                                                             
                                                                <div class="card" >
                                                                    <ul class="list-group list-group-flush">
                                                                        <li class="list-group-item">
                                                                            <b>Fecha: { lista.fecha}  </b><br>
                                                                            Lugar: {lista.lugar} <br>
                                                                            Tutor: {lista.display} <br>
                                                                            Obs: {lista.observacion} <br>

                                                                        </li>

                                     
                                                                    </ul>
                                                
                                                                  </div>
                                                                <!-- <span class="smaller"
                                                                    ><i class="bi bi-arrow-right-square" />
                                                                    </span
                                                                > -->
                                                            <!-- </div> -->
                                                        {/each}
                                                    </div>
                                                </div>
                                            </div>

                                            
                                        
                                            {/if}
										</td>
                                        <td class="fs-6  align-middle  border-top-0 text-center">
											{#if inscrito.actividades.calificar }
												{inscrito.nota}
											{/if}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{inscrito.actividades.fechainicio} <br> {inscrito.actividades.fechafin}

										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{inscrito.actividades.fecha_creacion} 
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{#if inscrito.actividades.general}
											<a class="btn btn-secondary" href="http://virtual.unemi.edu.ec/moodle/login/index.php" target="_blank" ><i class="fa fa-link"></i> Evaluar</a><br><br>
											{/if}
											{#if !inscrito.en_uso }
												{#if inscrito.puedeenviarsolicitudalumno }
												<!-- <a class="btn btn-danger" on:click={() => toggleModalFormulario()} ><i class="fa fa-link"></i> Enviar solicitud eliminación</a><br> -->
												<a class="btn btn-danger btn-sm" on:click={() => openEliminacionSolicitud(inscrito.actividades.display, inscrito.id)} > <i class="bi bi-folder-symlink"></i> Enviar solicitud eliminación</a><br>
												{/if}
											{/if}
										</td>
										

										
									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN INSCRIPCIONES EN ACTIVIADES COMPLEMENTARIAS ACTIVAS</td>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>
<br>
<br>


{#if eActividades.length > 0}
<div class="row">
	<div class="col-lg-12 col-xm-12 col-md-12">
		<div class="card">
            <div class="card-header text-center">
				<h4 class="mb-0 display-6">Actividades programadas</h4>
			</div>
			<div class="card-body">
				<div class="table-responsive">
					<input
						class="form-control"
						placeholder="Buscar actividad"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCongreso(value)}
					/>
					<table class="table mb-0 table-hover" id="rwd-table-congreso">
						<thead class="table-light">
							<tr>
								<th   style="width: 15px">Nº</th>

								<th scope="col" class="border-top-0 text-center align-middle " style="width: 15rem;"
									>Área</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Actividad / Facultad</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 35rem;"
									>Detalles</th
								>
								<th scope="col" class="border-top-0 text-center align-middle "
									>Fecha inicio / Fin inscripción</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " 
									>Cupo</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " 
									>Disponible</th
								>
								<th scope="col" class="border-top-0 text-center align-middle " 
									>Acciones</th
								>
							</tr>
						</thead>
						<tbody>
							{#if eActividades.length > 0}
								{#each eActividades as actividad, i}
								
									<tr>
										<td  style="width: 15px">
											{i+1}
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
											<img src="https://sga.unemi.edu.ec/static/images/iconos/actividades/{ actividad.periodoarea.areas.colorfondo }"> <strong>{actividad.periodoarea.areas.nombre}</strong> 
										</td>
                                        <td class="fs-6 align-middle border-top-0 ">
                                            <strong>[{actividad.idm}]</strong>
                                             {actividad.nombre} <br>
                                            {#if actividad.general}
                                                <span class="badge bg-info"> INDUCCIÓN GENERAL </span> <br>
                                            {/if}
                                            { actividad.coordinacion.display} 
                                            {#if actividad.nivelminimo && actividad.nivelmaximo }
                                            <br/><b>Nivel minimo:</b> { actividad.nivelminimo }
                                            <br/><b>Nivel maximo:</b>  { actividad.nivelmaximo }
                                            {#if actividad.nivel } <br/><b>Jornada:</b> { actividad.nivel.display } {/if}
                                            {/if }
                                            <br/><b>{ actividad.grupo_display }</b>

										</td>
									<td class="fs-6 text-justify">
                                            {actividad.descripcion}
                                            {#if actividad.link}
                                                <br>
                                                <b>link del evento: </b><a target="_blank" href="{ actividad.link }" >{ actividad.link }</a>
                                            {/if}
                                            
                                            {#if actividad.listafechas.length > 0 }
                                            <div class="accordion accordion-flush" id="accordionDocumentos">
                                                <div class="accordion-item" >
                                                    <h2
                                                        class="accordion-header" 
                                                        id="flush-heading-{actividad.idm}"
                                                    >
                                                        <button
                                                            class="accordion-button collapsed " style="height: 45px;"
                                                            type="button"
                                                            data-bs-toggle="collapse"
                                                            data-bs-target="#flush-collapse-{actividad.idm}"
                                                            aria-expanded="true"
                                                            aria-controls="flush-collapse-{actividad.idm}"
                                                        >
                                                        <h5>Horarios <i class="bi bi-calendar-range-fill" style="color:green"></i></h5> 
                                                        </button
                                                        >
                                                    </h2>
                                                    <div
                                                        id="flush-collapse-{actividad.idm}"
                                                        class="accordion-collapse collapse"
                                                        aria-labelledby="flush-heading-{actividad.idm}"
                                                        data-bs-parent="#accordionDocumentos"
                                                    >
                                                        {#each actividad.listafechas as lista}
                                                            <!-- <div class="accordion-body" style="text-align: left"> -->
                                                             
                                                                <div class="card" >
                                                                    <ul class="list-group list-group-flush">
                                                                        <li class="list-group-item">
                                                                            <b>Fecha: { lista.fecha}  </b><br>
                                                                            Lugar: {lista.lugar} <br>
                                                                            Tutor: {lista.display} <br>
                                                                            Obs: {lista.observacion} <br>

                                                                        </li>

                                     
                                                                    </ul>
                                                
                                                                  </div>
                                                                <!-- <span class="smaller"
                                                                    ><i class="bi bi-arrow-right-square" />
                                                                    </span
                                                                > -->
                                                            <!-- </div> -->
                                                        {/each}
                                                    </div>
                                                </div>
                                            </div>

                                            
                                        
                                            {/if}
										</td>
                                        <td class="fs-6  align-middle  border-top-0 text-center">
                                            {actividad.fechainicio} <br> {actividad.fechafin}
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
                                            <span class="badge bg-success"> {actividad.cupo}</span>
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
                                            <span class="badge bg-warning"> {actividad.restadisponibles}</span>
										</td>
                                        <td class="fs-6 align-middle border-top-0 text-center">
											{#if totalinscritosalu < maximo_actextracurricular }
												{#if actividad.entrefechas }
													{#if actividad.restadisponibles > 0}
														{#if actividad.carrera}
															{#if actividad.carrera == inscripcion.carrera}
																<div class="icon-shape icon-lg rounded-3 bg-light-success">
																	<a title="Seleccionar actividad"  on:click={() => confirmarInscripcion(actividad.id, actividad.nombre)}
																	
																	>
																		<svg
																			xmlns="http://www.w3.org/2000/svg"
																			width="24"
																			height="24"
																			fill="currentColor"
																			class="bi bi-file-pdf text-success"
																			viewBox="0 0 16 16"
																		>
																			<path
																				d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2zm10-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1z"
																			/>
																			<path d="M8.5 6a.5.5 0 0 0-1 0v1.5H6a.5.5 0 0 0 0 1h1.5V10a.5.5 0 0 0 1 0V8.5H10a.5.5 0 0 0 0-1H8.5V6z"/>

																		</svg>
																	</a>
																</div>
															{:else}
															No está disponible para su carrera
															{/if}
														{:else}
														<div class="icon-shape icon-lg rounded-3 bg-light-success">
															<a title="Seleccionar actividad" on:click={() => confirmarInscripcion(actividad.id, actividad.nombre)}
															
															>
																<svg
																	xmlns="http://www.w3.org/2000/svg"
																	width="24"
																	height="24"
																	fill="currentColor"
																	class="bi bi-file-pdf text-success"
																	viewBox="0 0 16 16"
																>
																	<path
																		d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2zm10-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1z"
																	/>
																	<path d="M8.5 6a.5.5 0 0 0-1 0v1.5H6a.5.5 0 0 0 0 1h1.5V10a.5.5 0 0 0 1 0V8.5H10a.5.5 0 0 0 0-1H8.5V6z"/>

																</svg>
															</a>
														</div>		
														{/if}
													{/if}
												{/if}
											{/if}
                                        </td>
										
									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN AREAS</td>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
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


<Modal
		isOpen={mOpenEliminacionSolicitud}
		toggle={mToggleEliminacionSolicitud}
		size={mSizeEliminacionSolicitud}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={mToggleEliminacionSolicitud}>
			<h4>Solicitud Eliminación</h4>
		</ModalHeader>
		<ModalBody>
			<form id="frmInfoPersonal" on:submit|preventDefault={saveInfoPersonal}>
				<div class="card-header text-center"> <h3> { nombrecabecera } </h3>  </div>
				<div class="card-body">
					<h4 class="">
						<strong>Ingresar una observación: </strong>
						
					</h4>
					<textarea
					rows="4" 
					cols="100"
					type="text"
					class="form-control"
					id="eObservacion"
					bind:value={observacion}
					/>
					<input
					type="text"
					class="form-control"
					id="eIdELiminar_2"
					bind:value={eIdELiminar}
					hidden
					/>
		
				
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeConfirmarMatricula()}>Cerrar</a>

					</div>
				</div>
					
			</form>
			
		</ModalBody>


</Modal>

<Modal isOpen={mOpenArchivoInscripcion}
		toggle={mToggleArchivoInscripcion}
		size={mSizeArchivoInscripcion}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}>

		<ModalHeader toggle={mToggleArchivoInscripcion}>
			<h4>Añadir documento de Inscripción</h4>
		</ModalHeader>
		<ModalBody>
			<form id="frmInfoArchivo" on:submit|preventDefault={saveInfoArchivo}>
				<div class="card-header text-center"> <h3> { nombrecabecera } </h3>  </div>
				<div class="card-body">
					<div class="col-md-4">

					<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Documento inscripción:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="ePersonaFileDocumento"
							bind:this={pondDocumento}
							{nameDocumento}
							name="fileDocumento"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFile}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxParallelUploads="1"
						/>
						<br>
						<br>
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						<input
						type="text"
						class="form-control"
						id="eIdInscripcion"
						bind:value={eIdInscripcion}
						hidden
						/>
		
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeArchivoInscripcion()}>Cerrar</a>

					</div>
				</div>
					
			</form>
			
		</ModalBody>


</Modal>


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

<style global>
	@import 'filepond/dist/filepond.css';

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
