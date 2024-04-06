<script lang="ts">
	import { apiPOST, apiPOSTFormData, browserGet, logOutUser } from '$lib/utils/requestUtils';

	import { loading } from '$lib/store/loadingStore';
	import Swal from 'sweetalert2';
	import { addNotification } from '$lib/store/notificationStore';
	import { goto } from '$app/navigation';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import Svelecte from 'svelecte';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';
	import { addToast } from '$lib/store/toastStore';
	const dispatch = createEventDispatcher();
	export let ePersona = undefined;
	export let ePerfilInscripcion = undefined;
	export let eRazas;
	export let eDiscapacidades;
	export let lEstadosPermanencia;
	export let ePaisesResidenciales;
	export let eMigrantePersona;
	export let eInstitucionDiscapacidades;
	export let eNacionalidadIndigenas;
	export let eCredos;
	export let ePersonaReligion;
	let sexo_id = 0;
	let nacimiento, email;
	let lgtbi,
		eszurda = false;
	let tieneDiscapacidad = false;
	let raza_id = 0;
	let nacionalidad_indigena_id = 0;
	let discapacidad_id = 0;
	let porcentaje_discapacidad = 0;
	let num_carnet_discapacidad;
	let entidad_valida_discapacidad;
	let es_ppl = false;
	let es_migrante = false;
	let fecha_ingreso;
	let fecha_retorno = '';
	let anios_residencia;
	let meses_residencia;
	let estado_permanencia = 1;
	let pais_residencia;
	let centro_rehabilitacion_social,
		lider_educativo,
		lider_educativo_correo,
		lider_educativo_telefono;
	let ppl_observacion = '';
	let credo_id = 1;
	let credo_prohibe = false;
	let credo_iglesia,
		credo_observacion = '';
	const dias = [
		{ value: 1, text: 'Lunes' },
		{ value: 2, text: 'Martes' },
		{ value: 3, text: 'Miércoles' },
		{ value: 4, text: 'Jueves' },
		{ value: 5, text: 'Viernes' },
		{ value: 6, text: 'Sábado' },
		{ value: 7, text: 'Domingo' }
	];

	overrideItemIdKeyNameBeforeInitialisingDndZones('value');
	let dias_value = [];
	let labelAsValue = false;
	let resetOnBlur = true;
	let tipoDocumentoGradoBachiller;
	onMount(async () => {
		registerPlugin(FilePondPluginFileValidateType);
		if (ePersona) {
			sexo_id = ePersona.sexo;
			nacimiento = ePersona.nacimiento;
			email = ePersona.email;
			lgtbi = ePersona.lgtbi;
			eszurda = ePersona.eszurda != undefined ? ePersona.eszurda : false;
		}
		if (ePerfilInscripcion) {
			tieneDiscapacidad = ePerfilInscripcion.tienediscapacidad
				? ePerfilInscripcion.tienediscapacidad
				: false;
			raza_id = ePerfilInscripcion.raza ? ePerfilInscripcion.raza : 0;
			nacionalidad_indigena_id = ePerfilInscripcion.nacionalidadindigena
				? ePerfilInscripcion.nacionalidadindigena
				: 0;
			discapacidad_id = ePerfilInscripcion.tipodiscapacidad
				? ePerfilInscripcion.tipodiscapacidad
				: 0;
			porcentaje_discapacidad = ePerfilInscripcion.porcientodiscapacidad
				? ePerfilInscripcion.porcientodiscapacidad
				: 0;
			num_carnet_discapacidad = ePerfilInscripcion.carnetdiscapacidad
				? ePerfilInscripcion.carnetdiscapacidad
				: '';
			entidad_valida_discapacidad = ePerfilInscripcion.institucionvalida
				? ePerfilInscripcion.institucionvalida
				: 0;
			credo_id = ePersona.credo ? ePersona.credo : 1;
			credo_prohibe = ePersonaReligion.prohibe;
			credo_iglesia = ePersonaReligion.iglesia;
			credo_observacion = ePersonaReligion.observacion;
			// dias_value = ePersonaReligion.dias ? ePersonaReligion.dias.split(',') : [6];
			console.log('dias:', ePersonaReligion.dias);
			if (ePersonaReligion.dias) {
				console.log('dd');
				const xDias = ePersonaReligion.dias.split(',');
				for (let index = 0; index < xDias.length; index++) {
					const e = xDias[index];
					dias.forEach((dia) => {
						if (dia.value === e) {
							dias_value.append(dia);
						}
					});
				}
			}
		}
		if( Object.keys(eMigrantePersona).length > 0){
			es_migrante = true;
			estado_permanencia = eMigrantePersona.estadopermanencia
			fecha_retorno = eMigrantePersona.fecharetorno
			meses_residencia = eMigrantePersona.mesresidencia
			anios_residencia = eMigrantePersona.anioresidencia
			pais_residencia = eMigrantePersona.paisresidenciaencr
			console.log(eMigrantePersona)
		}
	});

	// a reference to the component, used to call FilePond methods
	let pondDocumento;
	let pondEtnia;
	let pondDiscapacidad;
	let pondPPL;
	let pondMigrante;
	let pondCredo;
	let pondBachiller;

	//pondDocumento.acceptedFileTypes =  ['image/*'];

	// pond.getFiles() will return the active files

	// the name to use for the internal file input
	let nameDocumento = 'fileDocumento';
	let nameEtnia = 'fileEtnia';
	let nameDiscapacidad = 'fileDiscapacidad';
	let namePPL = 'filePPL';
	let nameMigrante = 'fileMigrante';
	let nameCredo = 'fileCredo';
	let nameBachiller = 'fileBachiller';

	// handle filepond events
	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondDocumento.getFiles());
		console.log('A file has been added', fileItem);
	};

	const saveInfoPersonal = async () => {
		const $frmInfoPersonal = document.querySelector('#frmInfoPersonal');
		const formData = new FormData($frmInfoPersonal);
		formData.append('action', 'saveInformacionPersonal');
		let fileDocumento = pondDocumento.getFiles();
		if (fileDocumento.length == 0) {
			addNotification({
				msg: 'Debe subir archivo de documento de cédula o pasaporte',
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
		if (!sexo_id || sexo_id === 0) {
			addNotification({
				msg: 'Favor complete el campo de sexo',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('sexo_id', sexo_id);
		}

		if (!nacimiento) {
			addNotification({
				msg: 'Favor complete el campo de fecha de nacimiento',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('nacimiento', nacimiento);
		}

		if (!email) {
			addNotification({
				msg: 'Favor complete el campo de correo personal',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('correo', email);
		}
		formData.append('lgtbi', lgtbi);
		formData.append('es_zurda', eszurda);

		if (!tipoDocumentoGradoBachiller){
			addNotification({
				msg: 'Favor complete el campo de tipo de documento de grado de bachiller',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}

		formData.append('tipoDocumentoGradoBachiller', tipoDocumentoGradoBachiller);

		let fileBachiller = pondBachiller.getFiles();
		if (fileBachiller.length == 0) {
			addNotification({
				msg: 'Debe subir archivo del tipo de documento de bachiller',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileBachiller.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let eFileBachiller = undefined;
		if (pondBachiller && pondBachiller.getFiles().length > 0) {
			eFileBachiller = pondBachiller.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileBachiller', eFileBachiller.file);

		if (!raza_id || raza_id === 10) {
			addNotification({
				msg: 'Favor complete el campo de etnia',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (raza_id === 1 && !nacionalidad_indigena_id) {
				addNotification({
					msg: 'Favor complete el campo de nacionalidad indígena',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				formData.append('nacionalidad_indigena_id', nacionalidad_indigena_id);
			}
		}
		formData.append('raza_id', raza_id);
		let eFileEtnia = undefined;
		if (pondEtnia && pondEtnia.getFiles().length > 0) {
			eFileEtnia = pondEtnia.getFiles()[0];
		}
		if (eFileEtnia) {
			formData.append('fileEtnia', eFileEtnia.file);
		}

		if (tieneDiscapacidad) {
			if (!discapacidad_id) {
				addNotification({
					msg: 'Favor complete el campo de tipo de discapacidad',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (!porcentaje_discapacidad) {
				addNotification({
					msg: 'Favor complete el campo de porcentaje de discapacidad',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (porcentaje_discapacidad <= 0 || porcentaje_discapacidad > 100) {
				addNotification({
					msg: 'Favor complete el campo de porcentaje de discapacidad debe ser mayor a 0 y menor a 100',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (!num_carnet_discapacidad) {
				addNotification({
					msg: 'Favor complete el campo de carnet de discapacidad',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (!entidad_valida_discapacidad) {
				addNotification({
					msg: 'Favor complete el campo de entidad que valida el carnet de discapacidad',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let fileDiscapacidad = pondDiscapacidad.getFiles();
			if (fileDiscapacidad.length == 0) {
				addNotification({
					msg: 'Debe subir archivo del carné de discapacidad',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileDiscapacidad.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileDiscapacidad = undefined;
			if (pondDiscapacidad && pondDiscapacidad.getFiles().length > 0) {
				eFileDiscapacidad = pondDiscapacidad.getFiles()[0];
			}

			formData.append('discapacidad_id', discapacidad_id);
			formData.append('porcentaje_discapacidad', porcentaje_discapacidad);
			formData.append('num_carnet_discapacidad', num_carnet_discapacidad);
			formData.append('entidad_valida_discapacidad', entidad_valida_discapacidad);
			if (eFileDiscapacidad) {
				formData.append('fileDiscapacidad', eFileDiscapacidad.file);
			}
		}
		if (es_ppl) {
			if (!fecha_ingreso) {
				addNotification({
					msg: 'Favor complete el campo de fecha de ingreso al centro de rehabilitación social',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (!centro_rehabilitacion_social) {
				addNotification({
					msg: 'Favor complete el campo de centro de rehabilitación social',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (!lider_educativo) {
				addNotification({
					msg: 'Favor complete el campo del lider educativo',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (!lider_educativo_correo) {
				addNotification({
					msg: 'Favor complete el campo del correo del lider educativo',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (!lider_educativo_telefono) {
				addNotification({
					msg: 'Favor complete el campo del teléfono del lider educativo',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			let filePPL = pondPPL.getFiles();
			if (filePPL.length == 0) {
				addNotification({
					msg: 'Debe subir archivo donde se evidencie que es un PPL',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (filePPL.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			let eFilePPL = undefined;
			if (pondPPL && pondPPL.getFiles().length > 0) {
				eFilePPL = pondPPL.getFiles()[0];
			}
			formData.append('fecha_ingreso', fecha_ingreso);
			formData.append('centro_rehabilitacion_social', centro_rehabilitacion_social);
			formData.append('lider_educativo', lider_educativo);
			formData.append('lider_educativo_correo', lider_educativo_correo);
			formData.append('lider_educativo_telefono', lider_educativo_telefono);
			formData.append('ppl_observacion', ppl_observacion);
			if (eFilePPL) {
				formData.append('filePPL', eFilePPL.file);
			}
		}
		if(es_migrante){
			if (!pais_residencia || pais_residencia == '0') {
				addNotification({
					msg: 'Favor complete el campo de País residencia en el pais que reside',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (!estado_permanencia) {
				addNotification({
					msg: 'Favor complete el campo de Estado permanencia en el pais que reside',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			// if (!fecha_retorno) {
			// 	addNotification({
			// 		msg: 'Favor complete el campo de Fecha de retorno en el pais que reside',
			// 		type: 'error',
			// 		target: 'newNotificationToast'
			// 	});
			// 	return;
			// }
			if (estado_permanencia == 1 ){
				if (!anios_residencia) {
					addNotification({
						msg: 'Favor complete el campo de Años de permanencia en el pais que reside',
						type: 'error',
						target: 'newNotificationToast'
					});
					return;
				}
				if (!meses_residencia) {
					addNotification({
						msg: 'Favor complete el campo de Meses de permanencia en el pais que reside',
						type: 'error',
						target: 'newNotificationToast'
					});
					return;
				}
			}
			let fileMigrante = pondMigrante.getFiles();
			if (fileMigrante.length == 0) {
				addNotification({
					msg: 'Debe subir Archivo contrato de vivienda/ servicios básicos',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			if (fileMigrante.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				return;
			}
			let eFileMigrante = undefined;
			if (pondMigrante && pondMigrante.getFiles().length > 0) {
				eFileMigrante = pondMigrante.getFiles()[0];
			}
			formData.append('pais_residencia', pais_residencia);
			formData.append('estado_permanencia', estado_permanencia);
			formData.append('fecha_retorno', fecha_retorno);

			if(estado_permanencia == 1){
				formData.append('anios_residencia', anios_residencia);
				formData.append('meses_residencia', meses_residencia);
			}
			if (eFileMigrante) {
				formData.append('fileMigrante', eFileMigrante.file);
			}
		}
		if (credo_prohibe) {
			if (!credo_iglesia) {
				addNotification({
					msg: 'Favor complete el campo de iglesia/institución',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (!dias_value || dias_value.length === 0) {
				addNotification({
					msg: 'Favor complete el campo de días',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let fileCredo = pondCredo.getFiles();
			if (fileCredo.length == 0) {
				addNotification({
					msg: 'Debe subir certificado emitido por la iglesia/institución',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileCredo.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileCredo = undefined;
			if (pondCredo && pondCredo.getFiles().length > 0) {
				eFileCredo = pondCredo.getFiles()[0];
			}

			formData.append('credo_iglesia', credo_iglesia);
			let dias_value_aux= [];
			dias_value.forEach(element => {
				dias_value_aux.push(element.value)
			});
			formData.append('credo_dias', JSON.stringify(dias_value_aux));
			if (credo_observacion) {
				formData.append('credo_observacion', credo_observacion);
			}
			if (eFileCredo) {
				formData.append('fileCredo', eFileCredo.file);
			}
		}
		formData.append('es_migrante', es_migrante);
		formData.append('es_ppl', es_ppl);
		formData.append('credo_id', credo_id);
		formData.append('tieneDiscapacidad', tieneDiscapacidad);
		formData.append('credo_prohibe', credo_prohibe);
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/matricula/admision', formData);

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
				return;
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};
</script>

<div class="text-center text-lg-start order-1 col-12 mt-4">
	<div class="card mb-3 ">
		<form id="frmInfoPersonal" on:submit|preventDefault={saveInfoPersonal}>
			<div class="card-header border-bottom px-4 py-3">
				<h4 class="text-primary">
					<div class="icon-shape icon-lg bg-primary text-white rounded-circle">1</div>
					Información personal
				</h4>
			</div>
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Datos personales</h3>
					<p class="mb-0">
						Actualizar información de campos obligatorios <span
							class="fs-bold text-danger">(*)</span
						>.
					</p>
				</div>
			</div>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-4">
						<label for="ePersonaNombres" class="form-label fw-bold">Nombres</label>
						<input
							type="text"
							class="form-control"
							id="ePersonaNombres"
							value={ePersona.nombres}
							disabled
							readonly
						/>
					</div>
					<div class="col-md-4">
						<label for="ePersonaApellido1" class="form-label fw-bold">Apellido paterno</label>
						<input
							type="text"
							class="form-control"
							id="ePersonaApellido1"
							value={ePersona.apellido1}
							disabled
							readonly
						/>
					</div>
					<div class="col-md-4">
						<label for="ePersonaApellido2" class="form-label fw-bold">Apellido materno</label>
						<input
							type="text"
							class="form-control"
							id="ePersonaApellido2"
							value={ePersona.apellido2}
							disabled
							readonly
						/>
					</div>
					<div class="col-md-4">
						<label for="ePersonaTipoDocumento" class="form-label fw-bold">Tipo documento:</label>
						<select
							class="form-control form-select"
							id="ePersonaTipoDocumento"
							name="ePersonaTipoDocumento"
							value={ePersona.tipo_documento}
							disabled
							readonly
						>
							{#each [{ value: '', text: 'NINGUNO' }, { value: 'CEDULA', text: 'CEDULA' }, { value: 'PASAPORTE', text: 'PASAPORTE' }] as tipo}
								<option value={tipo.value}>
									{tipo.text}
								</option>
							{/each}
						</select>
					</div>
					<div class="col-md-4">
						<label for="ePersonaDocumento" class="form-label fw-bold">Documento:</label>
						<input
							type="text"
							class="form-control"
							id="ePersonaDocumento"
							value={ePersona.documento}
							disabled
							readonly
						/>
					</div>
					<div class="col-md-4">
						<label for="ePersonaFileDocumento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Documento de identidad:</label
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
						<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
					</div>
					<div class="col-md-3">
						<label for="ePersonaSexo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Sexo:</label
						>

						<select class="form-control form-select" id="ePersonaSexo" bind:value={sexo_id}>
							{#each [{ value: 0, text: 'NINGUNO' }, { value: 1, text: 'MUJER' }, { value: 2, text: 'HOMBRE' }] as sexo}
								<option value={sexo.value}>
									{sexo.text}
								</option>
							{/each}
						</select>
					</div>
					<div class="col-md-3">
						<label for="ePersonaFechaNacimiento" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Fecha de nacimiento:</label
						>
						<input
							type="date"
							class="form-control flatpickr-input"
							id="ePersonaFechaNacimiento"
							bind:value={nacimiento}
						/>
					</div>
					<div class="col-md-6">
						<label for="ePersonaCorreo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Correo personal:</label
						>
						<input type="email" class="form-control" id="ePersonaCorreo" bind:value={email} />
					</div>
					<div class="col-md-2">
						<div class="form-check form-switch ">
							<input
								class="form-control form-check-input"
								type="checkbox"
								id="ePersonaLGTBI"
								bind:value={lgtbi}
							/>
							<label class="form-check-label" for="ePersonaLGTBI">LGTBI</label>
						</div>
					</div>
					<div class="col-md-2">
						<div class="form-check form-switch ">
							<input
								class="form-control form-check-input"
								type="checkbox"
								id="ePersonaEsZurda"
								bind:value={eszurda}
							/>
							<label class="form-check-label" for="ePersonaEsZurda">¿Es zurda?</label>
						</div>
					</div>
				</div>
			</div>
			<hr class="my-4" />
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Información académica</h3>
					<p class="mb-0">
						Carga obligatoria de documentos que certifiquen que el ciudadano ha obtenido su título de bachiller <span
							class="fs-bold text-danger">(*)</span
						>.
					</p>
				</div>
			</div>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-6">
						<label for="eRaza" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Tipo de documento de grado de bachiller:</label
						>
						<div class="form-check">
							<input
								class="form-check-input"
								type="radio"
								name="tipoDocumentoGradoBachiller"
								id="tipoDocumentoGradoBachillerActa"
								value={16}
								bind:group={tipoDocumentoGradoBachiller}
							/>
							<label class="form-check-label" for="tipoDocumentoGradoBachillerActa">
								ACTA DE GRADO DE BACHILLER
							</label>
						</div>
						<div class="form-check">
							<input
								class="form-check-input"
								type="radio"
								name="tipoDocumentoGradoBachiller"
								id="tipoDocumentoGradoBachillerTitulo"
								value={17}
								bind:group={tipoDocumentoGradoBachiller}
							/>
							<label class="form-check-label" for="tipoDocumentoGradoBachillerTitulo">
								TÍTULO DE BACHILLER
							</label>
						</div>
					</div>
					{#if tipoDocumentoGradoBachiller}
						<div class="col-md-6">
							<label for="fileBachiller" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span>
								{#if tipoDocumentoGradoBachiller === 16}
									Archivo de acta de grado de bachiller
								{:else}
									Archivo de titulo de bachiller
								{/if}
							</label>
							<FilePond
								class="pb-0 mb-0"
								bind:this={pondBachiller}
								id="fileBachiller"
								{nameBachiller}
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
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
					{/if}
				</div>
			</div>
			<hr class="my-4" />
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Etnia/Pueblo/Nacionalidad</h3>
					<p class="mb-0">
						Actualización obligatoria de información sobre etnia, pueblos y nacionalidades <span class="fs-bold text-danger">(*)</span>.
					</p>
				</div>
			</div>
			<div class="card-body">
				<div class="row g-3">
					<div class="col-md-4">
						<label for="eRaza" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Seleccionar etnia:</label
						>
						{#if eRazas.length > 0}
							<select class="form-control form-select" id="eRaza" bind:value={raza_id}>
								{#each eRazas as eRaza}
									<option value={eRaza.idm}>{eRaza.nombre}</option>
								{/each}
							</select>
						{/if}
					</div>
					{#if raza_id === 1}
						<div class="col-md-4">
							<label for="eNacionalidadIndigena" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Nacionalidad Indígena:</label
							>
							{#if eNacionalidadIndigenas.length > 0}
								<select
									class="form-control form-select"
									id="eNacionalidadIndigena"
									bind:value={nacionalidad_indigena_id}
								>
									{#each eNacionalidadIndigenas as eNacionalidadIndigena}
										<option value={eNacionalidadIndigena.idm}>{eNacionalidadIndigena.nombre}</option
										>
									{/each}
								</select>
							{/if}
						</div>
					{/if}
					{#if raza_id in [1, 2, 5]}
						<div class="col-md-4">
							<label for="eDiscapacidadFileDocumento" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Documento de etnia:</label
							>
							<FilePond
								id="eDiscapacidadFileDocumento"
								class="pb-0 mb-0"
								bind:this={pondEtnia}
								{nameEtnia}
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
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
					{/if}
				</div>
			</div>

			<hr class="my-4" />
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Discapacidad</h3>
					<!-- {#if tieneDiscapacidad}
						<p class="mb-0">
							Actualizar información obligatoria de discapacidad, campos obligatorios <span
								class="fs-bold text-danger">(*)</span
							>.
						</p>
					{/if} -->
					<div class="form-check form-switch ">
						<input
							class="form-control form-check-input"
							type="checkbox"
							id="ePersonaDiscapacidad"
							bind:checked={tieneDiscapacidad}
						/>
						<label class="form-check-label fs-bold" for="ePersonaDiscapacidad"
							>¿Tiene discapacidad?</label
						>
					</div>
				</div>
			</div>
			{#if tieneDiscapacidad}
				<div class="card-body">
					<div class="mb-2">
						<p class="mb-0">
							Ingreso obligatorio de información sobre discapacidad <span
								class="fs-bold text-danger">(*)</span
							>.
						</p>
					</div>
					<div class="row g-3">
						<div class="col-md-4">
							<label for="eDiscapacidadTipo" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Tipo:</label
							>
							{#if eDiscapacidades.length > 0}
								<select
									class="form-control form-select"
									id="eDiscapacidadTipo"
									bind:value={discapacidad_id}
								>
									{#each eDiscapacidades as eDiscapacidad}
										<option value={eDiscapacidad.idm}>{eDiscapacidad.nombre}</option>
									{/each}
								</select>
							{/if}
						</div>
						<div class="col-md-4">
							<label for="eDiscapacidadPorcentaje" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> % de Discapacidad:</label
							>
							<input
								type="number"
								class="form-control"
								id="eDiscapacidadPorcentaje"
								bind:value={porcentaje_discapacidad}
							/>
						</div>
						<div class="col-md-4">
							<label for="eDiscapacidadNumero" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> N° Carnet Discapacitado:</label
							>
							<input
								type="text"
								class="form-control"
								id="eDiscapacidadNumero"
								bind:value={num_carnet_discapacidad}
							/>
						</div>
						<div class="col-md-6">
							<label for="eDiscapacidadEntidad" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Institución emisora de carnet:</label
							>
							{#if eInstitucionDiscapacidades.length > 0}
								<select
									class="form-control form-select"
									id="eDiscapacidadEntidad"
									bind:value={entidad_valida_discapacidad}
								>
									{#each eInstitucionDiscapacidades as eInstitucionDiscapacidad}
										<option value={eInstitucionDiscapacidad.idm}
											>{eInstitucionDiscapacidad.nombre}</option
										>
									{/each}
								</select>
							{/if}
						</div>
						<div class="col-md-6">
							<label for="eDiscapacidadArchivo" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Archivo:</label
							>
							<FilePond
								class="pb-0 mb-0"
								id="eDiscapacidadArchivo"
								bind:this={pondDiscapacidad}
								{nameDiscapacidad}
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
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
					</div>
				</div>
			{/if}
			<hr class="my-4" />
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Religión/Credo</h3>
					<hr>
					<label for="eCredo" class="form-label fw-bold"
							> Seleccione una opción:</label
						>
					<div class="row g-3">
						<div class="col-md-4">
							{#if eCredos.length > 0}
								<select class="form-control form-select" id="eCredo" bind:value={credo_id}>
									{#each eCredos as eCredo}
										<option value={eCredo.idm}>{eCredo.nombre}</option>
									{/each}
								</select>
							{/if}
						</div>

						<div class="col-md-4">
							{#if credo_id != 1}
								<div class="form-check form-switch ">
									<input
										class="form-control form-check-input"
										type="checkbox"
										id="eReligionObliga"
										bind:checked={credo_prohibe}
									/>
									<label class="form-check-label fs-bold" for="eReligionObliga"
										>¿Religión/Credo no permite realizar actividades en días específicos?</label
									>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
			{#if credo_prohibe}
				<div class="card-body">
					<div class="mb-2">
						<p class="mb-0">
							Ingreso obligatorio de información sobre Religión/Credo <span
								class="fs-bold text-danger">(*)</span
							>.
						</p>
					</div>
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
							Documento emitido en hoja membretada por el Pastor de la Iglesia, sellado y firmado por él, donde certifique que tal o cual ciudadano tiene horarios en los cuales no podrá realizar ninguna actividad académica por dedicarse a practicar fielmente su culto.
						</div>
					</div>
					<div class="row g-3">
						<div class="col-md-8">
							<label for="eCredoIglesia" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span>Nombre de Iglesia o Institución:</label
							>
							<input
								type="text"
								class="form-control"
								id="eCredoIglesia"
								bind:value={credo_iglesia}
							/>
						</div>
						<div class="col-md-4">
							<label for="eCredoIglesia" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Días:</label
							>
							<Svelecte
								{resetOnBlur}
								options={dias}
								{labelAsValue}
								multiple
								bind:value={dias_value}
								valueAsObject
								{dndzone}
								placeholder="Seleccionar el/los días"
							/>
						</div>

						<div class="col-md-4">
							<label for="fileCredo" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Archivo de certificación de religión:</label
							>
							<FilePond
								class="pb-0 mb-0"
								bind:this={pondCredo}
								id="fileCredo"
								{nameCredo}
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
							<b><small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small></b>
						</div>
						<div class="col-md-8">
							<label for="eCredoObservacion" class="form-label fw-bold">Observación:</label>
							<textarea class="form-control" id="eCredoObservacion" minRows={4} maxRows={40}
								>{credo_observacion}</textarea
							>
						</div>
					</div>
				</div>
			{/if}
			<hr class="my-4" />
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Persona en el Exterior</h3>
					<div class="form-check form-switch ">
						<input
								class="form-control form-check-input"
								type="checkbox"
								id="ePersonaMigrante"
								bind:checked={es_migrante}
						/>
						<label class="form-check-label fs-bold" for="ePersonaPPL">¿Vive o Reside en otro Pais?</label>
					</div>
				</div>
			</div>
			{#if es_migrante}
				<div class="card-body">
					<div class="mb-2">
						<p class="mb-0">
							Ingreso obligatorio de información sobre el pais en el que vive o reside <span
								class="fs-bold text-danger">(*)</span
						>.
						</p>
					</div>
					<div class="row g-3">
						<div class="col-md-4">
							<label for="ePaisResidencia" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Pais residente:</label
							>
							{#if ePaisesResidenciales.length > 0}
								<select
										class="form-control form-select"
										id="ePaisResidencia"
										bind:value={pais_residencia}
								>
									<option value="0">-------------</option>
									{#each ePaisesResidenciales as pais}
										<option value={pais.id}>{pais.nombre}</option>
									{/each}
								</select>
							{/if}
						</div>
						<div class="col-md-4">
							<label for="eEstadoPermanencia" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Estado permanencia:</label
							>
							{#if lEstadosPermanencia.length > 0}
								<select
										class="form-control form-select"
										id="eEstadoPermanencia"
										bind:value={estado_permanencia}
								>
									{#each lEstadosPermanencia as estadopermanencia}
										<option value={estadopermanencia.id}>{estadopermanencia.name}</option>
									{/each}
								</select>
							{/if}
						</div>

							<div class="col-md-4">
								<label for="eMigranteFechaRetorno" class="form-label fw-bold"
								>Fecha de retorno:</label>
								<input
										type="date"
										class="form-control flatpickr-input"
										id="eMigranteFechaRetorno"
										bind:value={fecha_retorno}
								/>
							</div>
						{#if estado_permanencia !=2}
							<div class="col-md-3">
								<label for="eMigranteAnioResidencia" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Años permanencia:</label>
								<input
										type="number"
										class="form-control flatpickr-input"
										id="eMigranteAnioResidencia"
										bind:value={anios_residencia}
								/>
							</div>
							<div class="col-md-3">
								<label for="eMigranteMesesResidencia" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Meses permanencia:</label>
								<input
										type="number"
										class="form-control flatpickr-input"
										id="eMigranteMesesResidencia"
										bind:value={meses_residencia}
								/>
							</div>
						{/if}
						<div class="col-md-6">
							<label for="eMigranteArchivo" class="form-label fw-bold"
							><span class="fs-bold text-danger">(*)</span> Archivo  contrato de vivienda/ servicios básicos:</label
							>
							<FilePond
									class="pb-0 mb-0"
									id="eMigranteArchivo"
									bind:this={pondMigrante}
									{nameMigrante}
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
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
					</div>
				</div>
			{/if}
			<hr class="my-4" />
			<div class="card-header">
				<div class="mb-3 mb-lg-0">
					<h3 class="mb-0">Persona Privada de la Libertad</h3>
					<!-- {#if es_ppl}
						<p class="mb-0">
							Ingreso obligatorio de información sobre PPL <span
								class="fs-bold text-danger">(*)</span
							>.
						</p>
					{/if} -->
					<div class="form-check form-switch ">
						<input
							class="form-control form-check-input"
							type="checkbox"
							id="ePersonaPPL"
							bind:checked={es_ppl}
						/>
						<label class="form-check-label fs-bold" for="ePersonaPPL">¿Es PPL?</label>
					</div>
				</div>
			</div>
			{#if es_ppl}
				<div class="card-body">
					<div class="mb-2">
						<p class="mb-0">
							Ingreso obligatorio de información sobre PPL <span
								class="fs-bold text-danger">(*)</span
							>.
						</p>
					</div>
					<div class="row g-3">
						<div class="col-md-4">
							<label for="ePPLFechaIngreso" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Fecha de ingreso al CRS:</label
							>
							<input
								type="date"
								class="form-control flatpickr-input"
								id="ePPLFechaIngreso"
								bind:value={fecha_ingreso}
							/>
						</div>
						<div class="col-md-8">
							<label for="ePPLCentroRehabilitaciónSocial" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Centro de Rehabilitación Social:</label
							>
							<input
								type="text"
								class="form-control"
								id="ePPLCentroRehabilitaciónSocial"
								bind:value={centro_rehabilitacion_social}
							/>
						</div>
						<div class="col-md-6">
							<label for="ePPLLider" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Líder educativo:</label
							>
							<input type="text" class="form-control" id="ePPLLider" bind:value={lider_educativo} />
						</div>
						<div class="col-md-3">
							<label for="ePPLLiderCorreo" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Correo del líder educativo:</label
							>
							<input
								type="text"
								class="form-control"
								id="ePPLLiderCorreo"
								bind:value={lider_educativo_correo}
							/>
						</div>
						<div class="col-md-3">
							<label for="ePPLLiderTelefono" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Teléfono del líder educativo:</label
							>
							<input
								type="text"
								class="form-control"
								id="ePPLLiderTelefono"
								bind:value={lider_educativo_telefono}
							/>
						</div>
						<div class="col-md-6">
							<label for="ePPLObservacion" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Observación:</label
							>
							<textarea class="form-control" id="ePPLObservacion" minRows={4} maxRows={40}
								>{ppl_observacion}</textarea
							>
						</div>
						<div class="col-md-6">
							<label for="ePPLArchivo" class="form-label fw-bold"
								><span class="fs-bold text-danger">(*)</span> Archivo:</label
							>
							<FilePond
								class="pb-0 mb-0"
								id="ePPLArchivo"
								bind:this={pondPPL}
								{namePPL}
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
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
					</div>
				</div>
			{/if}
			<div class="card-footer text-muted">
				<div class="d-grid gap-2 d-md-flex justify-content-md-end">
					<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
					<button type="submit" class="btn btn-success">Siguiente</button>
				</div>
			</div>
		</form>
	</div>
</div>

<style global>
	@import 'filepond/dist/filepond.css';
</style>
