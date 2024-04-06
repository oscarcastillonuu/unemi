<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import {
		getTiposCursos as loadDataTiposCursos,
		getTiposCertificaciones as loadDataTiposCertificaciones,
		getTiposParticipaciones as loadDataTiposParticipaciones,
		getTiposCapacitaciones as loadDataTiposCapacitaciones,
		getContextosCapacitaciones as loadDataContextosCapacitaciones,
		getDetalleContextosCapacitaciones as loadDataDetalleContextosCapacitaciones,
		getAreasConocimientoTitulacion as loadDataAreasConocimientoTitulacion,
		getSubAreasConocimientoTitulacion as loadDataSubAreasConocimientoTitulacion,
		getSubAreasEspecificaConocimientoTitulacion as loadDataSubAreasEspecificaConocimientoTitulacion,
		getPaises as loadDataPaises,
		getProvinicias as loadDataProvincias,
		getCantones as loadDataCantones,
		getParroquias as loadDataParroquias
	} from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { cleave } from 'svelte-cleavejs'; //https://github.com/nosir/cleave.js/blob/master/doc/options.md
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
	export let mSize = 'xl';
	export let mOpenModal;
	export let mView = false;
	const eTipos = [
		{ id: 0, name: 'SIN DEFINIR' },
		{ id: 1, name: 'PEDAGÓGICA' },
		{ id: 2, name: 'CIENTÍFICA' }
	];
	const eModalidades = [
		{ id: 1, name: 'PRESENCIAL' },
		{ id: 2, name: 'SEMIPRESENCIAL' },
		{ id: 3, name: 'VIRTUAL' },
		{ id: 4, name: 'OTRA' },
		{ id: 5, name: 'PRESENCIAL/VIRTUAL' }
	];
	const flatpickrFechaInicioOptions = {
		element: '#id_fechainicio_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaFinOptions = {
		element: '#id_fechafin_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let eTiposCursos;
	let eTiposCertificaciones;
	let eTiposParticipaciones;
	let eTiposCapacitaciones;
	let eContextosCapacitaciones;
	let eDetallesContextosCapacitaciones;
	let eAreasConocimientoTitulacion;
	let eSubAreasConocimientoTitulacion;
	let eSubAreasEspecificaConocimientoTitulacion;
	let eCapacitacion;
	let inputInstitucion;
	let inputNombre;
	let inputDescripcion;
	let selectTipo = 0;
	let selectTipoCurso = 0;
	let selectTipoCertificacion = 0;
	let selectTipoParticipacion = 0;
	let selectTipoCapacitacion = 0;
	let selectModalidad = 0;
	let inputOtraModalidad = '';
	let selectContextoCapacitacion = 0;
	let selectDetalleContextoCapacitacion = 0;
	let selectAreaConocimientoTitulacion = 0;
	let selectSubAreaConocimientoTitulacion = 0;
	let selectSubAreaEspecificaConocimientoTitulacion = 0;
	let inputAuspiciante = '';
	let inputExpositor = '';
	let readSelectionPais = null;
	let readSelectionProvincia = null;
	let readSelectionCanton = null;
	let readSelectionParroquia = null;
	let inputFechaInicio = null;
	let inputFechaFin = null;
	let inputHoras = 0;
	let inputAnioInicio;
	let inputAnioFin;
	let download_archivo = '';
	let fileArchivo;
	let bloqueo = false;
	const dispatch = createEventDispatcher();

	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	onMount(async () => {
		eCapacitacion = aData.eCapacitacion ?? {};
		mensaje_load = 'Consultado la información, espere por favor...';
		eTiposCursos = await loadDataTiposCursos('');
		eTiposCertificaciones = await loadDataTiposCertificaciones('');
		eTiposParticipaciones = await loadDataTiposParticipaciones('');
		eTiposCapacitaciones = await loadDataTiposCapacitaciones('');
		eContextosCapacitaciones = await loadDataContextosCapacitaciones('');
		eDetallesContextosCapacitaciones = await loadDataDetalleContextosCapacitaciones('');
		eAreasConocimientoTitulacion = await loadDataAreasConocimientoTitulacion('');
		await delay(1000);
		if (eCapacitacion) {
			inputInstitucion = eCapacitacion.institucion ?? '';
			inputNombre = eCapacitacion.nombre ?? '';
			inputDescripcion = eCapacitacion.descripcion ?? '';
			selectTipo = eCapacitacion.tipo ?? 0;
			if (eCapacitacion.tipocurso) {
				selectTipoCurso = eCapacitacion.tipocurso.pk ?? 0;
			}
			if (eCapacitacion.tipocertificacion) {
				selectTipoCertificacion = eCapacitacion.tipocertificacion.pk ?? 0;
			}
			if (eCapacitacion.tipoparticipacion) {
				selectTipoParticipacion = eCapacitacion.tipoparticipacion.pk ?? 0;
			}
			if (eCapacitacion.tipocapacitacion) {
				selectTipoCapacitacion = eCapacitacion.tipocapacitacion.pk ?? 0;
			}
			selectModalidad = eCapacitacion.modalidad ?? 0;
			inputOtraModalidad = eCapacitacion.otramodalidad ?? '';
			if (eCapacitacion.contextocapacitacion) {
				selectContextoCapacitacion = eCapacitacion.contextocapacitacion.pk ?? 0;
			}

			if (eCapacitacion.detallecontextocapacitacion) {
				selectDetalleContextoCapacitacion = eCapacitacion.detallecontextocapacitacion.pk ?? 0;
			}
			if (eCapacitacion.areaconocimiento) {
				selectAreaConocimientoTitulacion = eCapacitacion.areaconocimiento.pk ?? 0;
			}
			if (eCapacitacion.subareaconocimiento) {
				eSubAreasConocimientoTitulacion = await loadDataSubAreasConocimientoTitulacion(
					'',
					selectAreaConocimientoTitulacion
				);
				selectSubAreaConocimientoTitulacion = eCapacitacion.subareaconocimiento.pk ?? 0;
			}
			if (eCapacitacion.subareaespecificaconocimiento) {
				eSubAreasEspecificaConocimientoTitulacion =
					await loadDataSubAreasEspecificaConocimientoTitulacion(
						'',
						selectSubAreaConocimientoTitulacion
					);
				selectSubAreaEspecificaConocimientoTitulacion =
					eCapacitacion.subareaespecificaconocimiento.pk ?? 0;
			}
			inputAuspiciante = eCapacitacion.auspiciante ?? '';
			inputExpositor = eCapacitacion.expositor ?? '';
			if (eCapacitacion.pais) {
				readSelectionPais = {
					id: eCapacitacion.pais['pk'],
					name: eCapacitacion.pais['nombre']
				};
			}
			if (eCapacitacion.provincia) {
				readSelectionProvincia = {
					id: eCapacitacion.provincia['pk'],
					name: eCapacitacion.provincia['nombre']
				};
			}
			if (eCapacitacion.canton) {
				readSelectionCanton = {
					id: eCapacitacion.canton['pk'],
					name: eCapacitacion.canton['nombre']
				};
			}
			if (eCapacitacion.parroquia) {
				readSelectionParroquia = {
					id: eCapacitacion.parroquia['pk'],
					name: eCapacitacion.parroquia['nombre']
				};
			}
			inputFechaInicio = eCapacitacion.fechainicio ?? null;
			inputFechaFin = eCapacitacion.fechafin ?? null;
			inputHoras = eCapacitacion.horas ?? 0;
			download_archivo = eCapacitacion.download_archivo ?? '';
			bloqueo = eCapacitacion.verificado;
		}
		mensaje_load = 'Cargando la información, espere por favor...';

		await delay(2000);
		load = false;
	});

	const saveFormacionAcademicaCapacitacion = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmCapacitacion = document.getElementById('frmCapacitacion');
		const formData = new FormData($frmCapacitacion);
		if (eCapacitacion != undefined) {
			formData.append('id', eCapacitacion.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('institucion', inputInstitucion);
		formData.append('nombre', inputNombre);
		formData.append('descripcion', inputDescripcion);
		formData.append('tipo', selectTipo.toString());
		formData.append('tipocurso', selectTipoCurso.toString());
		formData.append('tipoparticipacion', selectTipoParticipacion.toString());
		formData.append('tipocapacitacion', selectTipoCapacitacion.toString());
		formData.append('modalidad', selectModalidad.toString());
		formData.append('otramodalidad', inputOtraModalidad);
		formData.append('tipocertificacion', selectTipoCertificacion.toString());
		if (selectContextoCapacitacion != 0) {
			formData.append('contexto', selectContextoCapacitacion.toString());
		}
		if (selectDetalleContextoCapacitacion != 0) {
			formData.append('detallecontexto', selectDetalleContextoCapacitacion.toString());
		}

		formData.append('areaconocimiento', selectAreaConocimientoTitulacion.toString());
		formData.append('subareaconocimiento', selectSubAreaConocimientoTitulacion.toString());
		formData.append(
			'subareaespecificaconocimiento',
			selectSubAreaEspecificaConocimientoTitulacion.toString()
		);
		formData.append('auspiciante', inputAuspiciante);
		formData.append('expositor', inputExpositor);
		if (readSelectionPais != null) {
			formData.append('pais', readSelectionPais.id);
		}
		if (readSelectionProvincia != null) {
			formData.append('provincia', readSelectionProvincia.id);
		}
		if (readSelectionCanton != null) {
			formData.append('canton', readSelectionCanton.id);
		}
		if (readSelectionParroquia != null) {
			formData.append('parroquia', readSelectionParroquia.id);
		}
		const fechaInicio = document.getElementById('id_fechainicio');
		if (fechaInicio) {
			formData.append('fechainicio', fechaInicio.value);
		}
		const fechaFin = document.getElementById('id_fechafin');
		if (fechaFin) {
			formData.append('fechafin', fechaFin.value);
		}
		formData.append('horas', inputHoras.toString());
		if (fileArchivo) {
			formData.append('archivo', fileArchivo.file);
		}

		formData.append('action', 'saveFormacionAcademicaCapacitacion');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/hoja_vida', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (!res.isSuccess) {
				addToast({ type: 'error', header: '¡ERROR!', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				if (res.data.form) {
					await customFormErrors(res.data.form);
				}

				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'saveFormacionAcademicaCapacitacion' });
			}
		}
	};

	const changeAreaConocimientoTitulacion = async (event) => {
		//console.log("change: ", event);
		selectSubAreaConocimientoTitulacion = 0;
		selectSubAreaEspecificaConocimientoTitulacion = 0;
		eSubAreasConocimientoTitulacion = await loadDataSubAreasConocimientoTitulacion(
			'',
			event.target.value
		);
	};

	const changeSubAreaConocimientoTitulacion = async (event) => {
		//console.log("change: ", event);
		selectSubAreaEspecificaConocimientoTitulacion = 0;
		eSubAreasEspecificaConocimientoTitulacion =
			await loadDataSubAreasEspecificaConocimientoTitulacion('', event.target.value);
	};

	const changePais = (event) => {
		//console.log("change pais: ", event);
		readSelectionProvincia = null;
		readSelectionCanton = null;
		readSelectionParroquia = null;
	};

	const changeProvincia = (event) => {
		//console.log("change provincia: ", event);
		readSelectionCanton = null;
		readSelectionParroquia = null;
	};

	const changeCanton = (event) => {
		//console.log("change canton: ", event);
		readSelectionParroquia = null;
	};

	const handleFileSelectedArchivo = (event) => {
		fileArchivo = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileArchivo = null;
	};

	const actionEdit = () => {
		mView = !mView;
		mTitle = `Editar capacitación ${inputNombre}`;
	};
</script>

{#if eCapacitacion}
	<Modal isOpen={mOpenModal} toggle={mToggle} size={mSize} class={mClass} backdrop="static">
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmCapacitacion">
					<div class="row">
						<label
							for="id_institucion"
							class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
							>Institución <span><i class="fe fe-alert-octagon text-warning" /></span>
						</label>
						<div class="col-sm-9 m-auto">
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_institucion"
								disabled={mView}
								bind:value={inputInstitucion}
							/>
						</div>
						<div class="col-sm-12 valid-feedback" id="id_institucion_validate">¡Se ve bien!</div>
					</div>
					<div class="row">
						<label
							for="id_nombre"
							class="col-sm-3 col-form-label text-sm-end text-start  fw-bold text-black"
							>Nombre del evento <span><i class="fe fe-alert-octagon text-warning" /></span>
						</label>
						<div class="col-sm-9 m-auto">
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_nombre"
								disabled={mView}
								bind:value={inputNombre}
							/>
						</div>
						<div class="col-sm-12 valid-feedback" id="id_nombre_validate">¡Se ve bien!</div>
					</div>
					<div class="row">
						<label
							for="id_descripcion"
							class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
							>Descripción del evento <span><i class="fe fe-alert-octagon text-warning" /></span>
						</label>
						<div class="col-sm-9 m-auto">
							<textarea
								class="form-control"
								id="id_descripcion"
								disabled={mView}
								value={inputDescripcion}
							/>
						</div>
						<div class="col-sm-12 valid-feedback" id="id_descripcion_validate">¡Se ve bien!</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_tipo"
									class="col-sm-3 col-md-6  col-form-label text-sm-end text-start fw-bold text-black"
									>Tipo de evento <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6  m-auto">
									{#if eTipos}
										<select
											class="form-select form-select-sm"
											aria-label=""
											disabled={mView}
											id="id_tipo"
											bind:value={selectTipo}
										>
											<option value={0} selected> ----------- </option>
											{#each eTipos as eTipo}
												{#if selectTipo === eTipo.id}
													<option value={eTipo.id} selected>
														{eTipo.name}
													</option>
												{:else}
													<option value={eTipo.id}>
														{eTipo.name}
													</option>
												{/if}
											{/each}
										</select>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_tipo_validate">¡Se ve bien!</div>
							</div>
						</div>
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_tipocurso"
									class="col-sm-3 col-md-6  col-form-label text-sm-end text-start fw-bold text-black"
									>Tipo de capacitación <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6  m-auto">
									{#if eTiposCursos}
										<select
											class="form-select form-select-sm"
											aria-label=""
											disabled={mView}
											id="id_tipocurso"
											bind:value={selectTipoCurso}
										>
											<option value={0} selected> ----------- </option>
											{#each eTiposCursos as eTipo}
												{#if selectTipoCurso === eTipo.id}
													<option value={eTipo.id} selected>
														{eTipo.name}
													</option>
												{:else}
													<option value={eTipo.id}>
														{eTipo.name}
													</option>
												{/if}
											{/each}
										</select>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_tipocurso_validate">¡Se ve bien!</div>
							</div>
						</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_tipoparticipacion"
									class="col-sm-3 col-md-6  col-form-label text-sm-end text-start fw-bold text-black"
									>Tipo de certificación <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6  m-auto">
									{#if eTiposParticipaciones}
										<select
											class="form-select form-select-sm"
											aria-label=""
											disabled={mView}
											id="id_tipoparticipacion"
											bind:value={selectTipoParticipacion}
										>
											<option value={0} selected> ----------- </option>
											{#each eTiposParticipaciones as eTipo}
												{#if selectTipoParticipacion === eTipo.id}
													<option value={eTipo.id} selected>
														{eTipo.name}
													</option>
												{:else}
													<option value={eTipo.id}>
														{eTipo.name}
													</option>
												{/if}
											{/each}
										</select>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_tipoparticipacion_validate">
									¡Se ve bien!
								</div>
							</div>
						</div>
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_tipocapacitacion"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Programado plan Institucional <span
										><i class="fe fe-alert-octagon text-warning" /></span
									>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									{#if eTiposCapacitaciones}
										<select
											class="form-select form-select-sm"
											aria-label=""
											disabled={mView}
											id="id_tipocapacitacion"
											bind:value={selectTipoCapacitacion}
										>
											<option value={0} selected> ----------- </option>
											{#each eTiposCapacitaciones as eTipo}
												{#if selectTipoCapacitacion === eTipo.id}
													<option value={eTipo.id} selected>
														{eTipo.name}
													</option>
												{:else}
													<option value={eTipo.id}>
														{eTipo.name}
													</option>
												{/if}
											{/each}
										</select>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_tipocapacitacion_validate">
									¡Se ve bien!
								</div>
							</div>
						</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_modalidad"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Modalidad <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									{#if eModalidades}
										<select
											class="form-select form-select-sm"
											aria-label=""
											disabled={mView}
											id="id_modalidad"
											bind:value={selectModalidad}
										>
											<option value={0} selected> ----------- </option>
											{#each eModalidades as eTipo}
												{#if selectModalidad === eTipo.id}
													<option value={eTipo.id} selected>
														{eTipo.name}
													</option>
												{:else}
													<option value={eTipo.id}>
														{eTipo.name}
													</option>
												{/if}
											{/each}
										</select>
									{/if}
									{#if selectModalidad === 4}
										<input
											type="text"
											class="form-control form-control-sm"
											id="id_otramodalidad"
											disabled={mView}
											bind:value={inputOtraModalidad}
										/>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_modalidad_validate">¡Se ve bien!</div>
							</div>
						</div>
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_tipocertificacion"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Tipo de planificación <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									{#if eTiposCertificaciones}
										<select
											class="form-select form-select-sm"
											aria-label=""
											disabled={mView}
											id="id_tipocertificacion"
											bind:value={selectTipoCertificacion}
										>
											<option value={0} selected> ----------- </option>
											{#each eTiposCertificaciones as eTipo}
												{#if selectTipoCertificacion === eTipo.id}
													<option value={eTipo.id} selected>
														{eTipo.name}
													</option>
												{:else}
													<option value={eTipo.id}>
														{eTipo.name}
													</option>
												{/if}
											{/each}
										</select>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_tipocertificacion_validate">
									¡Se ve bien!
								</div>
							</div>
						</div>
					</div>
					<div class="row">
						<label
							for="id_contexto"
							class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
							>Contexto de la capacitación/formación
						</label>
						<div class="col-sm-9 m-auto">
							{#if eContextosCapacitaciones}
								<select
									class="form-select form-select-sm"
									aria-label=""
									disabled={mView}
									id="id_contexto"
									bind:value={selectContextoCapacitacion}
								>
									<option value={0} selected> ----------- </option>
									{#each eContextosCapacitaciones as eContexto}
										{#if selectContextoCapacitacion === eContexto.id}
											<option value={eContexto.id} selected>
												{eContexto.name}
											</option>
										{:else}
											<option value={eContexto.id}>
												{eContexto.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
						</div>
						<div class="col-sm-12 valid-feedback" id="id_contexto_validate">¡Se ve bien!</div>
					</div>
					{#if selectContextoCapacitacion == 1}
						<div class="row">
							<label
								for="id_detallecontexto"
								class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
								>Detalle de contexto
							</label>
							<div class="col-sm-9 m-auto">
								{#if eDetallesContextosCapacitaciones}
									<select
										class="form-select form-select-sm"
										aria-label=""
										disabled={mView}
										id="id_detallecontexto"
										bind:value={selectDetalleContextoCapacitacion}
									>
										<option value={0} selected> ----------- </option>
										{#each eDetallesContextosCapacitaciones as eDetalle}
											{#if selectDetalleContextoCapacitacion === eDetalle.id}
												<option value={eDetalle.id} selected>
													{eDetalle.name}
												</option>
											{:else}
												<option value={eDetalle.id}>
													{eDetalle.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
							</div>
							<div class="col-sm-12 valid-feedback" id="id_detallecontexto_validate">
								¡Se ve bien!
							</div>
						</div>
					{/if}
					<div class="row">
						<label
							for="id_areaconocimiento"
							class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
							>Área conocimiento
						</label>
						<div class="col-sm-9 m-auto">
							{#if eAreasConocimientoTitulacion}
								<select
									class="form-select form-select-sm"
									aria-label=""
									disabled={mView}
									id="id_areaconocimiento"
									on:change={changeAreaConocimientoTitulacion}
									bind:value={selectAreaConocimientoTitulacion}
								>
									<option value={0} selected> ----------- </option>
									{#each eAreasConocimientoTitulacion as eArea}
										{#if selectAreaConocimientoTitulacion === eArea.id}
											<option value={eArea.id} selected>
												{eArea.name}
											</option>
										{:else}
											<option value={eArea.id}>
												{eArea.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
						</div>
						<div class="col-sm-12 valid-feedback" id="id_areaconocimiento_validate">
							¡Se ve bien!
						</div>
					</div>
					{#if selectAreaConocimientoTitulacion != 0}
						<div class="row">
							<label
								for="id_subareaconocimiento"
								class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
								>Sub área conocimiento
							</label>
							<div class="col-sm-9 m-auto">
								{#if eSubAreasConocimientoTitulacion}
									<select
										class="form-select form-select-sm"
										aria-label=""
										disabled={mView}
										id="id_subareaconocimiento"
										on:change={changeSubAreaConocimientoTitulacion}
										bind:value={selectSubAreaConocimientoTitulacion}
									>
										<option value={0} selected> ----------- </option>
										{#each eSubAreasConocimientoTitulacion as eSubArea}
											{#if selectSubAreaConocimientoTitulacion === eSubArea.id}
												<option value={eSubArea.id} selected>
													{eSubArea.name}
												</option>
											{:else}
												<option value={eSubArea.id}>
													{eSubArea.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
							</div>
							<div class="col-sm-12 valid-feedback" id="id_subareaconocimiento_validate">
								¡Se ve bien!
							</div>
						</div>
					{/if}
					{#if selectSubAreaConocimientoTitulacion != 0}
						<div class="row">
							<label
								for="id_subareaespecificaconocimiento"
								class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
								>Sub área especifica conocimiento
							</label>
							<div class="col-sm-9 m-auto">
								{#if eSubAreasEspecificaConocimientoTitulacion}
									<select
										class="form-select form-select-sm"
										aria-label=""
										disabled={mView}
										id="id_subareaespecificaconocimiento"
										bind:value={selectSubAreaEspecificaConocimientoTitulacion}
									>
										<option value={0} selected> ----------- </option>
										{#each eSubAreasEspecificaConocimientoTitulacion as eSubArea}
											{#if selectSubAreaEspecificaConocimientoTitulacion === eSubArea.id}
												<option value={eSubArea.id} selected>
													{eSubArea.name}
												</option>
											{:else}
												<option value={eSubArea.id}>
													{eSubArea.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
							</div>
							<div class="col-sm-12 valid-feedback" id="id_subareaespecificaconocimiento_validate">
								¡Se ve bien!
							</div>
						</div>
					{/if}
					<div class="row">
						<label
							for="id_auspiciante"
							class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
							>Auspiciante
						</label>
						<div class="col-sm-9 m-auto">
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_auspiciante"
								disabled={mView}
								bind:value={inputAuspiciante}
							/>
						</div>
						<div class="col-sm-12 valid-feedback" id="id_auspiciante_validate">¡Se ve bien!</div>
					</div>
					<div class="row">
						<label
							for="id_expositor"
							class="col-sm-3 col-form-label text-sm-end text-start fw-bold text-black"
							>Expositor
						</label>
						<div class="col-sm-9 m-auto">
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_expositor"
								disabled={mView}
								bind:value={inputExpositor}
							/>
						</div>
						<div class="col-sm-12 valid-feedback" id="id_expositor_validate">¡Se ve bien!</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_pais"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>País <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									<FormSelectSearch
										inputId="id_pais"
										name="pais"
										disabled={mView}
										minQuery={1}
										bind:value={readSelectionPais}
										on:actionChangeSelectSearch={changePais}
										fetch={(query) => loadDataPaises(query)}
									/>
								</div>
								<div class="col-sm-12 valid-feedback" id="id_pais_validate">¡Se ve bien!</div>
							</div>
						</div>
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_provincia"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Provincia
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									<FormSelectSearch
										inputId="id_provincia"
										name="provincia"
										parent="id_pais"
										minQuery={1}
										disabled={mView ? true : readSelectionPais === null}
										bind:value={readSelectionProvincia}
										on:actionChangeSelectSearch={changeProvincia}
										fetch={(query) => loadDataProvincias(readSelectionPais.id, query)}
									/>
								</div>
								<div class="col-sm-12 valid-feedback" id="id_provincia_validate">¡Se ve bien!</div>
							</div>
						</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_canton"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Cantón
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									<FormSelectSearch
										inputId="id_canton"
										name="canton"
										parent="id_provincia"
										minQuery={1}
										disabled={mView ? true : readSelectionProvincia === null}
										bind:value={readSelectionCanton}
										on:actionChangeSelectSearch={changeCanton}
										fetch={(query) => loadDataCantones(readSelectionProvincia.id, query)}
									/>
								</div>
								<div class="col-sm-12 valid-feedback" id="id_canton_validate">¡Se ve bien!</div>
							</div>
						</div>
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_parroquia"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Parroquia
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									<FormSelectSearch
										inputId="id_parroquia"
										name="parroquia"
										parent="id_canton"
										minQuery={1}
										disabled={mView ? true : readSelectionCanton === null}
										bind:value={readSelectionParroquia}
										fetch={(query) => loadDataParroquias(readSelectionCanton.id, query)}
									/>
								</div>
								<div class="col-sm-12 valid-feedback" id="id_parroquia_validate">¡Se ve bien!</div>
							</div>
						</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_fechainicio"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Fecha inicio <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									{#if mView}
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											readonly={true}
											disabled={true}
											bind:value={inputFechaInicio}
											id="id_fechainicio"
										/>
									{:else}
										<Flatpickr
											options={flatpickrFechaInicioOptions}
											bind:value={inputFechaInicio}
											element="#id_fechainicio_element"
										>
											<div class="flatpickr input-group" id="id_fechainicio_element">
												<input
													type="text"
													class="form-control form-control-sm"
													placeholder=""
													data-input
													id="id_fechainicio"
												/>
												<span class="input-group-text text-muted" title="Fecha" data-toggle
													><i class="fe fe-calendar" /></span
												>
												<span class="input-group-text text-danger" title="clear" data-clear>
													<i class="fe fe-x" />
												</span>
											</div>
										</Flatpickr>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_fechainicio_validate">
									¡Se ve bien!
								</div>
							</div>
						</div>
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_fechafin"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Fecha fin <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									{#if mView}
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											readonly={true}
											disabled={true}
											bind:value={inputFechaFin}
											id="id_fechafin"
										/>
									{:else}
										<Flatpickr
											options={flatpickrFechaFinOptions}
											bind:value={inputFechaFin}
											element="#id_fechafin_element"
										>
											<div class="flatpickr input-group" id="id_fechafin_element">
												<input
													type="text"
													class="form-control form-control-sm"
													placeholder=""
													data-input
													id="id_fechafin"
												/>
												<span class="input-group-text text-muted" title="Fecha" data-toggle
													><i class="fe fe-calendar" /></span
												>
												<span class="input-group-text text-danger" title="clear" data-clear>
													<i class="fe fe-x" />
												</span>
											</div>
										</Flatpickr>
									{/if}
								</div>
								<div class="col-sm-12 valid-feedback" id="id_fechafin_validate">¡Se ve bien!</div>
							</div>
						</div>
					</div>
					<div class="row">
						<div class="col-md-6">
							<div class="row">
								<label
									for="id_horas"
									class="col-sm-3 col-md-6 col-form-label text-sm-end text-start fw-bold text-black"
									>Horas <span><i class="fe fe-alert-octagon text-warning" /></span>
								</label>
								<div class="col-sm-9 col-md-6 m-auto">
									<input
										type="text"
										class="form-control form-control-sm"
										placeholder=""
										id="id_horas"
										disabled={mView}
										use:cleave={{
											numeral: true,
											numeralDecimalMark: ',',
											numeralIntegerScale: 4,
											numeralDecimalScale: 0,
											numeralPositiveOnly: true,
											delimiter: '.'
										}}
										bind:value={inputHoras}
									/>
								</div>
								<div class="col-sm-12 valid-feedback" id="id_horas_validate">¡Se ve bien!</div>
							</div>
						</div>
					</div>
					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-md-6 col-12">
							<label for="id_archivo" class="form-label fw-bold">Archivo</label>
							{#if !mView}
								<FileUploader
									inputID="id_archivo"
									inputName="archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedArchivo}
									on:fileRemoved={handleFileRemovedArchivo}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if download_archivo != ''}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={download_archivo}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{:else if mView}
								<div class="fs-6">
									<p class="fw-bold text-danger">No tienes archivo subido</p>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivo_validate">¡Se ve bien!</div>
						</div>
					</div>
				</form>
			{:else}
				<div class="m-0 my-5 justify-content-center align-items-center">
					<div class="text-center align-middle">
						<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
						<h3>{mensaje_load}</h3>
					</div>
				</div>
			{/if}
		</ModalBody>
		<ModalFooter>
			{#if !load}
				{#if !eCapacitacion.verificado}
					{#if !mView}
						<Button
							color="warning"
							class="rounded-5 btn-sm"
							on:click={saveFormacionAcademicaCapacitacion}
							><i class="fe fe-check" /> Guardar</Button
						>
					{:else}
						<Button type="button" color="primary" class="rounded-5 btn-sm" on:click={actionEdit}
							><i class="fe fe-edit" /> Editar</Button
						>
					{/if}
				{/if}
			{/if}

			<Button color="secondary" class="rounded-5 btn-sm" on:click={mToggle}
				><i class="fe fe-x" /> Cancelar</Button
			>
		</ModalFooter>
	</Modal>
{/if}

<style>
	.form-select {
		border-color: #aaa;
	}
	.form-control {
		border-color: #aaa;
	}
</style>
