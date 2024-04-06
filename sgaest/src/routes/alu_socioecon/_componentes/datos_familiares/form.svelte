<script lang="ts">
	import { apiPOST, apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	import {
		getParentescos as loadParentescos,
		getNivelesTitulacion as loadNivelesTitulacion,
		getFormasTrabajo as loadFormasTrabajo,
		getDiscapacidades as loadDiscapacidades,
		getInstitucionesDiscapacidad as loadInstitucionesDiscapacidades
	} from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { addNotification } from '$lib/store/notificationStore';
	export let aData;
	export let mToggle;
	let ePersonaDatosFamiliar;
	let ePersona;
	const dispatch = createEventDispatcher();
	const flatpickrOptions = {
		element: '#id_nacimiento_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let id = 0;
	let fileIdentificacion;
	let fileDiscapacidad;
	let fileAutorizado;
	let titulo = '';
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let eParentescos;
	let eNivelTitulaciones;
	let eFormasTrabajo;
	let eDiscapacidades;
	let eInstitucionesDiscapacidad;
	let inputIdentificacion = '';
	let inputNombre = '';
	let selectParentesco = 0;
	let inputNacimiento = '';
	let selectRangoEdad = 0;
	let inputFallecido = false;
	let inputTelefono = '';
	let inputTelefonoConv = '';
	let inputTrabajo = '';
	let inputConvive = false;
	let inputSustentoHogar = false;
	let selectNivelTitulacion = 0;
	let selectFormaTrabajo = 0;
	let inputIngresoMensual = 0;
	let download_identificacion = '';
	let download_discapacidad = '';
	let download_autorizadoministerio = '';
	let selectTipoInstitucionLaboral = 0;
	let inputTieneNegocio = false;
	let inputNegocio = '';
	let inputTieneDiscapacidad = false;
	let selectTipoDiscapacidad = 0;
	let inputPorcientoDiscapacidad = 0;
	let inputCarnetDiscapacidad = '';
	let selectInstitucionDiscapacidad = 0;
	let inputEsSustituto = false;
	let RangosEdades = [
		{ id: 0, text: `Ninguno` },
		{ id: 1, text: `De 1 a 12 meses` },
		{ id: 2, text: `De 13 a 24 meses` },
		{ id: 3, text: `De 25 a 36 meses` },
		{ id: 4, text: `Mayor de 36 meses` }
	];
	let TiposInstitucionesLaboral = [
		{ id: 0, text: `-------` },
		{ id: 1, text: `SECTOR PÚBLICO` },
		{ id: 2, text: `SECTOR PRIVADO` }
	];
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		titulo = 'Adicionar dato familiar';
		mensaje_load = 'Consultado la información, espere por favor...';
		eParentescos = await loadParentescos();
		eNivelTitulaciones = await loadNivelesTitulacion();
		eFormasTrabajo = await loadFormasTrabajo();
		eDiscapacidades = await loadDiscapacidades();
		eInstitucionesDiscapacidad = await loadInstitucionesDiscapacidades();
		ePersonaDatosFamiliar = aData.ePersonaDatosFamiliar;
		ePersona = aData.ePersona;
		if (ePersonaDatosFamiliar) {
			id = ePersonaDatosFamiliar.pk;
			titulo = 'Actualizar dato familiar';
			inputIdentificacion = ePersonaDatosFamiliar.identificacion;
			inputNombre = ePersonaDatosFamiliar.nombre;
			if (ePersonaDatosFamiliar.parentesco) {
				selectParentesco = ePersonaDatosFamiliar.parentesco['pk'] ?? 0;
			}
			inputNacimiento = ePersonaDatosFamiliar.nacimiento;
			selectRangoEdad = ePersonaDatosFamiliar.rangoedad ?? 0;
			inputFallecido = ePersonaDatosFamiliar.fallecido;
			inputTelefono = ePersonaDatosFamiliar.telefono;
			inputTelefonoConv = ePersonaDatosFamiliar.telefono_conv;
			inputTrabajo = ePersonaDatosFamiliar.trabajo;
			inputConvive = ePersonaDatosFamiliar.convive;
			inputSustentoHogar = ePersonaDatosFamiliar.sustentohogar;
			if (ePersonaDatosFamiliar.niveltitulacion) {
				selectNivelTitulacion = ePersonaDatosFamiliar.niveltitulacion['pk'] ?? 0;
			}
			if (ePersonaDatosFamiliar.formatrabajo) {
				selectFormaTrabajo = ePersonaDatosFamiliar.formatrabajo['pk'] ?? 0;
			}
			inputIngresoMensual = ePersonaDatosFamiliar.ingresomensual;
			if (ePersonaDatosFamiliar.download_identificacion) {
				download_identificacion = ePersonaDatosFamiliar.download_identificacion;
			}
			inputTieneNegocio = ePersonaDatosFamiliar.tienenegocio;
			inputNegocio = ePersonaDatosFamiliar.negocio;
			inputTieneDiscapacidad = ePersonaDatosFamiliar.tienediscapacidad;
			if (ePersonaDatosFamiliar.tipodiscapacidad) {
				selectTipoDiscapacidad = ePersonaDatosFamiliar.tipodiscapacidad['pk'] ?? '';
			}
			inputPorcientoDiscapacidad = ePersonaDatosFamiliar.porcientodiscapacidad ?? 0;
			inputCarnetDiscapacidad = ePersonaDatosFamiliar.carnetdiscapacidad;
			if (ePersonaDatosFamiliar.institucionvalida) {
				selectInstitucionDiscapacidad = ePersonaDatosFamiliar.institucionvalida['pk'] ?? '';
			}
			selectTipoInstitucionLaboral = ePersonaDatosFamiliar.tipoinstitucionlaboral ?? 0;
			if (ePersonaDatosFamiliar.download_discapacidad) {
				download_discapacidad = ePersonaDatosFamiliar.download_discapacidad;
			}
			inputEsSustituto = ePersonaDatosFamiliar.essustituto;
			if (ePersonaDatosFamiliar.download_autorizadoministerio) {
				download_autorizadoministerio = ePersonaDatosFamiliar.download_autorizadoministerio;
			}
		}
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(2000);
		load = false;
	});

	const handleBlurIdentificacion = async (event) => {
		const value = event.target.value;
		document.getElementById(`id_nombre`).readOnly = false;
		const field = document.getElementById(`id_identificacion`);
		const validate = document.getElementById(`id_identificacion_validate`);
		if (field != undefined) {
			if (field.classList.contains('is-invalid')) {
				field.classList.remove('is-invalid');
			}

			if (field.classList.contains('is-valid')) {
				field.classList.remove('is-valid');
			}
			//field.classList.add('is-valid');
		}
		if (validate != undefined) {
			if (validate.classList.contains('valid-feedback')) {
				validate.classList.remove('valid-feedback');
			}

			if (validate.classList.contains('invalid-feedback')) {
				validate.classList.remove('invalid-feedback');
			}
			validate.classList.add('valid-feedback');
			validate.textContent = '';
		}
		if (ePersona.identificacion == value) {
			addToast({
				type: 'error',
				header: 'Identificación',
				body: `Número de documento ${value} no puede ingresar su propia identificación`
			});
			inputNombre = '';
			document.getElementById(`id_nombre`).readOnly = true;

			if (field != undefined) {
				if (field.classList.contains('is-invalid')) {
					field.classList.remove('is-invalid');
				}

				if (field.classList.contains('is-valid')) {
					field.classList.remove('is-valid');
				}

				field.classList.add('is-invalid');
			}
			if (validate != undefined) {
				if (validate.classList.contains('valid-feedback')) {
					validate.classList.remove('valid-feedback');
				}

				if (validate.classList.contains('invalid-feedback')) {
					validate.classList.remove('invalid-feedback');
				}

				validate.classList.add('invalid-feedback');
				validate.textContent = `No puede agregar su propia identificación.`;
			}
			return;
		} else if (value.length != 0) {
			loading.setLoading(true, 'Consultando, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
				action: 'loadDatosPersona',
				identificacion: value
			});
			loading.setLoading(false, 'Consultando, espere por favor...');
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
					inputNombre = res.data.ePersona.nombre_completo;
					inputNacimiento = res.data.ePersona.nacimiento;
					inputTelefono = res.data.ePersona.telefono;
					inputTelefonoConv = res.data.ePersona.telefono_conv;
				}
			}
		}
	};

	const saveDatosFamiliar = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosFamiliar = document.getElementById('frmDatosFamiliar');
		const formData = new FormData($frmDatosFamiliar);
		//const numeros = /^([0-9])*$/;

		const fecha = document.getElementById('id_nacimiento');
		formData.append('id', id.toString());
		formData.append('identificacion', inputIdentificacion);
		formData.append('nombre', inputNombre);
		if (fileIdentificacion) {
			formData.append('cedulaidentidad', fileIdentificacion.file);
		}
		if (selectParentesco != 0) {
			formData.append('parentesco', selectParentesco.toString());
		}
		formData.append('nacimiento', fecha.value);
		formData.append('rangoedad', selectRangoEdad.toString());
		formData.append('fallecido', inputFallecido ? 'true' : 'false');
		formData.append('telefono', inputTelefono);
		formData.append('telefono_conv', inputTelefonoConv);
		formData.append('trabajo', inputTrabajo);
		formData.append('convive', inputConvive ? 'true' : 'false');
		formData.append('sustentohogar', inputSustentoHogar ? 'true' : 'false');
		if (selectNivelTitulacion != 0) {
			formData.append('niveltitulacion', selectNivelTitulacion.toString());
		}
		if (selectFormaTrabajo != 0) {
			formData.append('formatrabajo', selectFormaTrabajo.toString());
		}
		formData.append('ingresomensual', inputIngresoMensual.toString());
		formData.append('tipoinstitucionlaboral', selectTipoInstitucionLaboral.toString());
		formData.append('tienenegocio', inputTieneNegocio ? 'true' : 'false');
		formData.append('negocio', inputNegocio);
		formData.append('tienediscapacidad', inputTieneDiscapacidad ? 'true' : 'false');
		if (selectTipoDiscapacidad != 0) {
			formData.append('tipodiscapacidad', selectTipoDiscapacidad.toString());
		}
		formData.append('porcientodiscapacidad', inputPorcientoDiscapacidad.toString());
		formData.append('carnetdiscapacidad', inputCarnetDiscapacidad.toString());
		if (selectInstitucionDiscapacidad != 0) {
			formData.append('institucionvalida', selectInstitucionDiscapacidad.toString());
		}
		if (fileDiscapacidad) {
			formData.append('ceduladiscapacidad', fileDiscapacidad.file);
		}
		formData.append('essustituto', inputEsSustituto ? 'true' : 'false');
		if (fileAutorizado) {
			formData.append('autorizadoministerio', fileAutorizado.file);
		}

		formData.append('action', 'saveDatosFamiliar');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/socioeconomica', formData);
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
				dispatch('actionRun', { action: 'saveDatosFamiliar' });
			}
		}
	};

	const handleFileSelectedIdentificacion = (event) => {
		fileIdentificacion = event.detail;
	};

	const handleFileRemovedIdentificacion = () => {
		fileIdentificacion = null;
	};

	const handleFileSelectedDiscapacidad = (event) => {
		fileDiscapacidad = event.detail;
	};

	const handleFileRemovedDiscapacidad = () => {
		fileDiscapacidad = null;
	};

	const handleFileSelectedAutorizado = (event) => {
		fileAutorizado = event.detail;
	};

	const handleFileRemovedAutorizado = () => {
		fileAutorizado = null;
	};

	const onChangeSustituto = (event) => {
		inputEsSustituto = event.target.checked;
	};

	const onChangeFallecido = (event) => {
		inputFallecido = event.target.checked;
	};

	const onChangeTieneNegocioPropio = (event) => {
		inputTieneNegocio = event.target.checked;
	};

	const onChangeTieneDiscapacidad = (event) => {
		inputTieneDiscapacidad = event.target.checked;
	};
</script>

<Modal
	isOpen={true}
	toggle={mToggle}
	size="xl"
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down"
	backdrop="static"
>
	<ModalHeader toggle={mToggle} class="bg-primary text-white">
		<span class="text-white">{titulo}</span>
	</ModalHeader>
	<ModalBody>
		{#if !load}
			<form action="javascript:;" id="frmDatosFamiliar">
				<div class="row g-3">
					<div class="col-md-3 col-lg-3 col-sm-3">
						<label for="id_identificacion" class="form-label fw-bold">Identificación:</label>
						<input
							type="text"
							class="form-control form-control-sm"
							id="id_identificacion"
							bind:value={inputIdentificacion}
							on:blur={handleBlurIdentificacion}
						/>
						<div class="valid-feedback" id="id_identificacion_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-9 col-lg-9 col-sm-9">
						<label for="id_nombre" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Nombres/Apellidos:</label
						>
						<input
							type="text"
							class="form-control form-control-sm"
							id="id_nombre"
							bind:value={inputNombre}
						/>
						<div class="valid-feedback" id="id_nombre_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-12 col-lg-12 col-sm-12">
						<label for="id_cedulaidentidad" class="form-label fw-bold"
							>Archivo identificación:</label
						>
						<FileUploader
							inputID="id_identificacion_archivo"
							inputName="cedulaidentidad"
							acceptedFileTypes={['application/pdf']}
							labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
							on:fileSelected={handleFileSelectedIdentificacion}
							on:fileRemoved={handleFileRemovedIdentificacion}
						/>
						<div class="text-center fs-6">
							<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
						{#if download_identificacion != ''}
							<div class="fs-6">
								Tienes un archivo subido:
								<a
									title="Ver archivo"
									href={download_identificacion}
									target="_blank"
									class="text-primary text-center">Ver archivo</a
								>
							</div>
						{/if}

						<div class="valid-feedback" id="id_cedulaidentidad_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4 col-lg-3 col-sm-6">
						<label for="id_parentesco" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Parentesco:</label
						>
						{#if eParentescos}
							<select
								class="form-select form-select-sm"
								aria-label=""
								id="id_parentesco"
								bind:value={selectParentesco}
							>
								<option value={0} selected> ----------- </option>
								{#each eParentescos as eParentesco}
									{#if selectParentesco === eParentesco.id}
										<option value={eParentesco.id} selected>
											{eParentesco.name}
										</option>
									{:else}
										<option value={eParentesco.id}>
											{eParentesco.name}
										</option>
									{/if}
								{/each}
							</select>
						{/if}
						<div class="valid-feedback" id="id_parentesco_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4 col-lg-5 col-sm-6">
						<label for="id_nacimiento" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha de nacimiento:</label
						>
						<Flatpickr
							options={flatpickrOptions}
							bind:value={inputNacimiento}
							element="#id_nacimiento_element"
						>
							<div class="flatpickr input-group" id="id_nacimiento_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_nacimiento"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_nacimiento_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4 col-lg-4 col-sm-6">
						<label for="id_rangoedad" class="form-label fw-bold">Rango de edad:</label>
						<select
							class="form-select form-select-sm"
							aria-label=""
							id="id_rangoedad"
							bind:value={selectRangoEdad}
						>
							{#each RangosEdades as rango}
								{#if selectRangoEdad === rango.id}
									<option value={rango.id} selected>
										{rango.text}
									</option>
								{:else}
									<option value={rango.id}>
										{rango.text}
									</option>
								{/if}
							{/each}
						</select>
						<div class="valid-feedback" id="id_rangoedad_validate">¡Se ve bien!</div>
					</div>

					<div class="col-md-12 col-lg-12 col-sm-12">
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="id_fallecido"
								bind:value={inputFallecido}
								on:change={onChangeFallecido}
							/>
							<label class="form-check-label fw-bold text-dark" for="id_fallecido"
								>¿Esta fallecido?</label
							>
						</div>
						<div class="valid-feedback" id="id_fallecido_validate">¡Se ve bien!</div>
					</div>
					{#if !inputFallecido}
						<div class="col-md-3 col-lg-3 col-sm-6">
							<label for="id_telefono" class="form-label fw-bold">Telefono celular:</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_telefono"
								bind:value={inputTelefono}
							/>
							<div class="valid-feedback" id="id_telefono_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-3 col-lg-3 col-sm-6">
							<label for="id_telefono_conv" class="form-label fw-bold">Telefono fija:</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_telefono_conv"
								bind:value={inputTelefonoConv}
							/>
							<div class="valid-feedback" id="id_telefono_conv_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6 col-lg-6 col-sm-12">
							<label for="id_trabajo" class="form-label fw-bold">Lugar de Trabajo:</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_trabajo"
								bind:value={inputTrabajo}
							/>
							<div class="valid-feedback" id="id_trabajo_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6 col-lg-6 col-sm-6">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_convive"
									bind:checked={inputConvive}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_convive"
									>¿Convive con usted?</label
								>
							</div>
							<div class="valid-feedback" id="id_convive_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6 col-lg-6 col-sm-6">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_sustentohogar"
									bind:checked={inputSustentoHogar}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_sustentohogar"
									>¿Es sustento del hogar?</label
								>
							</div>
							<div class="valid-feedback" id="id_sustentohogar_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6 col-lg-6 col-sm-6">
							<label for="id_niveltitulacion" class="form-label fw-bold">Nivel Titulacion:</label>
							{#if eNivelTitulaciones}
								<select
									class="form-select form-select-sm"
									aria-label=""
									id="id_niveltitulacion"
									bind:value={selectNivelTitulacion}
								>
									<option value={0} selected> ----------- </option>
									{#each eNivelTitulaciones as eNivel}
										{#if selectNivelTitulacion === eNivel.id}
											<option value={eNivel.id} selected>
												{eNivel.name}
											</option>
										{:else}
											<option value={eNivel.id}>
												{eNivel.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_niveltitulacion_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-4 col-lg-3 col-sm-6">
							<label for="id_formatrabajo" class="form-label fw-bold">Tipo Trabajo:</label>
							{#if eFormasTrabajo}
								<select
									class="form-select form-select-sm"
									aria-label=""
									id="id_formatrabajo"
									bind:value={selectFormaTrabajo}
								>
									<option value={0} selected> ----------- </option>
									{#each eFormasTrabajo as eFormaTrabajo}
										{#if selectFormaTrabajo === eFormaTrabajo.id}
											<option value={eFormaTrabajo.id} selected>
												{eFormaTrabajo.name}
											</option>
										{:else}
											<option value={eFormaTrabajo.id}>
												{eFormaTrabajo.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_formatrabajo_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-3 col-lg-3 col-sm-12">
							<label for="id_ingresomensual" class="form-label fw-bold">Ingreso mensual:</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_ingresomensual"
								bind:value={inputIngresoMensual}
							/>
							<div class="valid-feedback" id="id_ingresomensual_validate">¡Se ve bien!</div>
						</div>
					{/if}
				</div>
				{#if !inputFallecido}
					<hr />
					<h5 class="fw-bold text-primary">Situación laboral del familiar</h5>
					<div class="row g-3">
						<div class="col-md-12 col-lg-12 col-sm-12">
							<label for="id_tipoinstitucionlaboral" class="form-label fw-bold">
								Tipo de Institución Laboral:</label
							>
							{#if TiposInstitucionesLaboral}
								<select
									class="form-select form-select-sm"
									aria-label=""
									id="id_tipoinstitucionlaboral"
									bind:value={selectTipoInstitucionLaboral}
								>
									{#each TiposInstitucionesLaboral as Tipo}
										{#if selectTipoInstitucionLaboral === Tipo.id}
											<option value={Tipo.id} selected>
												{Tipo.text}
											</option>
										{:else}
											<option value={Tipo.id}>
												{Tipo.text}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_tipoinstitucionlaboral_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-12 col-lg-6 col-sm-12">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_tienenegocio"
									bind:checked={inputTieneNegocio}
									on:change={onChangeTieneNegocioPropio}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_tienenegocio"
									>¿Tiene negocio propio?</label
								>
							</div>
							<div class="valid-feedback" id="id_tienenegocio_validate">¡Se ve bien!</div>
						</div>
						{#if inputTieneNegocio}
							<div class="col-md-12 col-lg-12 col-sm-12">
								<label for="id_negocio" class="form-label fw-bold">Descripción de Negocio:</label>
								<input
									type="text"
									class="form-control form-control-sm"
									id="id_negocio"
									bind:value={inputNegocio}
								/>
								<div class="valid-feedback" id="id_negocio_validate">¡Se ve bien!</div>
							</div>
						{/if}
					</div>
					<hr />
					<h5 class="fw-bold text-primary">Datos de discapacidad del familiar</h5>
					<div class="row g-3">
						<div class="col-md-12 col-lg-12 col-sm-12">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_tienediscapacidad"
									bind:checked={inputTieneDiscapacidad}
									on:change={onChangeTieneDiscapacidad}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_tienediscapacidad"
									>¿Tiene discapacidad?</label
								>
							</div>
							<div class="valid-feedback" id="id_tienediscapacidad_validate">¡Se ve bien!</div>
						</div>
						{#if inputTieneDiscapacidad}
							<div class="col-md-4 col-lg-4 col-sm-12">
								<label for="id_tipodiscapacidad" class="form-label fw-bold">Tipo:</label>
								{#if eDiscapacidades}
									<select
										class="form-select form-select-sm"
										aria-label=""
										id="id_tipodiscapacidad"
										bind:value={selectTipoDiscapacidad}
									>
										<option value={0} selected> ----------- </option>
										{#each eDiscapacidades as eDiscapacidad}
											{#if selectTipoDiscapacidad === eDiscapacidad.id}
												<option value={eDiscapacidad.id} selected>
													{eDiscapacidad.name}
												</option>
											{:else}
												<option value={eDiscapacidad.id}>
													{eDiscapacidad.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
								<div class="valid-feedback" id="id_tipodiscapacidad_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-4 col-lg-4 col-sm-12">
								<label for="id_porcientodiscapacidad" class="form-label fw-bold">Porcentaje:</label>
								<input
									type="text"
									class="form-control form-control-sm"
									id="id_porcientodiscapacidad"
									bind:value={inputPorcientoDiscapacidad}
								/>
								<div class="valid-feedback" id="id_porcientodiscapacidad_validate">
									¡Se ve bien!
								</div>
							</div>
							<div class="col-md-4 col-lg-4 col-sm-4">
								<label for="id_carnetdiscapacidad" class="form-label fw-bold">Nro carné:</label>
								<input
									type="text"
									class="form-control form-control-sm"
									id="id_carnetdiscapacidad"
									bind:value={inputCarnetDiscapacidad}
								/>
								<div class="valid-feedback" id="id_carnetdiscapacidad_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-12 col-lg-12 col-sm-12">
								<label for="id_institucionvalida" class="form-label fw-bold"
									>Institución Valida:</label
								>
								{#if eInstitucionesDiscapacidad}
									<select
										class="form-select form-select-sm"
										aria-label=""
										id="id_institucionvalida"
										bind:value={selectInstitucionDiscapacidad}
									>
										<option value={0} selected> ----------- </option>
										{#each eInstitucionesDiscapacidad as eInstitucion}
											{#if selectInstitucionDiscapacidad === eInstitucion.id}
												<option value={eInstitucion.id} selected>
													{eInstitucion.name}
												</option>
											{:else}
												<option value={eInstitucion.id}>
													{eInstitucion.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
								<div class="valid-feedback" id="id_institucionvalida_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-12 col-lg-12 col-sm-12">
								<label for="id_discapacidad_archivo" class="form-label fw-bold"
									>Archivo del carné:</label
								>
								<FileUploader
									inputID="id_discapacidad_archivo"
									inputName="discapacidad_archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedDiscapacidad}
									on:fileRemoved={handleFileRemovedDiscapacidad}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
								{#if download_discapacidad != ''}
									<div class="fs-6">
										Tienes un archivo subido:
										<a
											title="Ver archivo"
											href={download_discapacidad}
											target="_blank"
											class="text-primary text-center">Ver archivo</a
										>
									</div>
								{/if}

								<div class="valid-feedback" id="id_discapacidad_archivo_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-12 col-lg-12 col-sm-12">
								<div class="form-check form-switch">
									<input
										class="form-check-input"
										type="checkbox"
										id="id_essustituto"
										bind:checked={inputEsSustituto}
										on:change={onChangeSustituto}
									/>
									<label class="form-check-label fw-bold text-dark" for="id_essustituto"
										>¿Es sustituto?</label
									>
								</div>
								<div class="valid-feedback" id="id_essustituto_validate">¡Se ve bien!</div>
							</div>
							{#if inputEsSustituto}
								<div class="col-md-12 col-lg-12 col-sm-12">
									<label for="id_autorizadoministerio_archivo" class="form-label fw-bold"
										>Archivo autorizado por ministerio:</label
									>
									<FileUploader
										inputID="id_autorizadoministerio_archivo"
										inputName="autorizadoministerio_archivo"
										acceptedFileTypes={['application/pdf']}
										labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
										on:fileSelected={handleFileSelectedAutorizado}
										on:fileRemoved={handleFileRemovedAutorizado}
									/>
									<div class="text-center fs-6">
										<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small
										>
									</div>
									{#if download_autorizadoministerio != ''}
										<div class="fs-6">
											Tienes un archivo subido:
											<a
												title="Ver archivo"
												href={download_autorizadoministerio}
												target="_blank"
												class="text-primary text-center">Ver archivo</a
											>
										</div>
									{/if}

									<div class="valid-feedback" id="id_autorizadoministerio_archivo_validate">
										¡Se ve bien!
									</div>
								</div>
							{/if}
						{/if}
					</div>
				{/if}
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
		<Button color="secondary" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
		{#if !load}
			<Button color="primary" class="rounded-3 btn-sm" on:click={saveDatosFamiliar}>Guardar</Button>
		{/if}
	</ModalFooter>
</Modal>


<style>
	.form-select {
		border-color: #aaa;
	}
	.form-control {
		border-color: #aaa;
	}
</style>