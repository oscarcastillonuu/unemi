<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
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
	import { getEstadoCivil as loadEstadoCivil, getSexos as loadSexos } from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';

	export let aData;
	export let mToggle;
	let ePersona;
	let eEstadosCivil;
	let eSexos;
	const dispatch = createEventDispatcher();
	const flatpickrOptions = {
		element: '#id_nacimiento_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputNombres = '';
	let inputApellido1 = '';
	let inputApellido2 = '';
	let inputTipoDocumento = '';
	let inputDocumento = '';
	let selectEstadoCivil = '';
	let selectSexo = '';
	let inputFechaNacimiento = null;
	let inputLibretaMilitar = '';
	let inputEmail = '';
	let inputLGTBI = false;
	let inputZurda = false;
	let fileDocumento;
	let filePapeleta;
	let fileLibretaMilitar;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePersona = aData.ePersona;
		mensaje_load = 'Consultado la información, espere por favor...';
		eEstadosCivil = await loadEstadoCivil();
		eSexos = await loadSexos();
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		inputNombres = ePersona.nombres;
		inputApellido1 = ePersona.apellido1;
		inputApellido2 = ePersona.apellido2;
		inputTipoDocumento = ePersona.tipo_documento;
		inputDocumento = ePersona.documento;
		const estado_civil = ePersona.estado_civil;
		if (ePersona.estado_civil) {
			selectEstadoCivil = estado_civil['pk'] ?? '';
		}
		const sexo = ePersona.sexo;
		if (ePersona.sexo) {
			selectSexo = sexo['pk'] ?? '';
		}
		inputFechaNacimiento = ePersona.nacimiento;
		inputEmail = ePersona.email;
		inputLibretaMilitar = ePersona.libretamilitar;
		inputLGTBI = ePersona.lgtbi;
		inputZurda = ePersona.eszurdo;
		await delay(2000);
		load = false;
	});

	const saveDatosPersonales = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosPersonales = document.getElementById('frmDatosPersonales');
		const formData = new FormData($frmDatosPersonales);
		//const numeros = /^([0-9])*$/;
		const fecha = document.getElementById('id_nacimiento');

		formData.append('estadocivil', selectEstadoCivil);
		formData.append('sexo', selectSexo);
		formData.append('nacimiento', fecha.value);
		formData.append('email', inputEmail);
		formData.append('libretamilitar', inputLibretaMilitar);
		formData.append('lgtbi', inputLGTBI ? 'true' : 'false');
		formData.append('eszurdo', inputZurda ? 'true' : 'false');
		if (fileDocumento) {
			formData.append('documento_archivo', fileDocumento.file);
		}
		if (filePapeleta) {
			formData.append('papeleta_archivo', filePapeleta.file);
		}
		if (fileLibretaMilitar) {
			formData.append('libretamilitar_archivo', fileLibretaMilitar.file);
		}

		formData.append('action', 'saveDatosPersonales');
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
				dispatch('actionRun', { action: 'saveDatosPersonales' });
			}
		}
	};

	const handleFileSelectedDocumento = (event) => {
		fileDocumento = event.detail;
	};

	const handleFileRemovedDocumento = () => {
		fileDocumento = null;
	};

	const handleFileSelectedPapeleta = (event) => {
		filePapeleta = event.detail;
	};

	const handleFileRemovedPapeleta = () => {
		filePapeleta = null;
	};
	const handleFileSelectedLibretaMilitar = (event) => {
		fileLibretaMilitar = event.detail;
	};

	const handleFileRemovedLibretaMilitar = () => {
		fileLibretaMilitar = null;
	};
</script>

{#if ePersona}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size="lg"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">Actualizar datos personales</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
			<form action="javascript:;" id="frmDatosPersonales">
				<div class="row g-3">
					<div class="col-md-3">
						<label for="id_nombre" class="form-label fw-bold">Nombres:</label>
						<input
							type="text"
							readonly
							class="form-control-plaintext form-control-sm"
							id="id_nombre"
							bind:value={inputNombres}
						/>
					</div>
					<div class="col-md-3">
						<label for="id_apellido1" class="form-label fw-bold">Primer Apellido:</label>
						<input
							type="text"
							readonly
							class="form-control-plaintext form-control-sm"
							id="id_apellido1"
							bind:value={inputApellido1}
						/>
					</div>
					<div class="col-md-3">
						<label for="id_apellido2" class="form-label fw-bold">Segundo Apellido:</label>
						<input
							type="text"
							readonly
							class="form-control-plaintext form-control-sm"
							id="id_apellido2"
							bind:value={inputApellido2}
						/>
					</div>
					<div class="col-md-3">
						<label for="id_documento" class="form-label fw-bold">{inputTipoDocumento}:</label>
						<input
							type="text"
							readonly
							class="form-control-plaintext form-control-sm"
							id="id_documento"
							bind:value={inputDocumento}
						/>
					</div>
					<div class="col-md-4">
						<label for="id_estadocivil" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Estado civil:</label
						>
						{#if eEstadosCivil}
							<select
								class="form-select"
								aria-label=""
								required
								id="id_estadocivil"
								bind:value={selectEstadoCivil}
							>
								{#each eEstadosCivil as eEstadoCivil}
									{#if selectEstadoCivil === eEstadoCivil.id}
										<option value={eEstadoCivil.id} selected>
											{eEstadoCivil.name}
										</option>
									{:else}
										<option value={eEstadoCivil.id}>
											{eEstadoCivil.name}
										</option>
									{/if}
								{/each}
							</select>
						{/if}
						<div class="valid-feedback" id="id_estadocivil_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4">
						<label for="id_sexo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Sexo:</label
						>
						{#if eSexos}
							<select
								class="form-select"
								aria-label=""
								required
								id="id_sexo"
								bind:value={selectSexo}
							>
								{#each eSexos as eSexo}
									{#if selectSexo === eSexo.id}
										<option value={eSexo.id} selected>
											{eSexo.name}
										</option>
									{:else}
										<option value={eSexo.id}>
											{eSexo.name}
										</option>
									{/if}
								{/each}
							</select>
						{/if}
						<div class="valid-feedback" id="id_sexo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4">
						<label for="id_nacimiento" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha de nacimiento:</label
						>
						<Flatpickr
							options={flatpickrOptions}
							bind:value={inputFechaNacimiento}
							element="#id_nacimiento_element"
						>
							<div class="flatpickr input-group" id="id_nacimiento_element">
								<input
									type="text"
									class="form-control"
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
					<div class="col-md-8">
						<label for="id_email" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Correo electrónico personal:</label
						>
						<input type="email" class="form-control" id="id_email" bind:value={inputEmail} />
						<div class="valid-feedback" id="id_email_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4">
						<label for="id_libretamilitar" class="form-label fw-bold">Libreta militar:</label>
						<input
							type="text"
							class="form-control"
							id="id_libretamilitar"
							bind:value={inputLibretaMilitar}
						/>
						<div class="valid-feedback" id="id_libretamilitar_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6">
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="id_lgtbi"
								bind:checked={inputLGTBI}
							/>
							<label class="form-check-label fw-bold  text-dark" for="id_lgtbi"
								>¿Pertenece al Grupo LGTBI?</label
							>
						</div>
						<div class="valid-feedback" id="id_lgtbi_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6">
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="id_eszurdo"
								bind:checked={inputZurda}
							/>
							<label class="form-check-label fw-bold text-dark" for="id_eszurdo">¿Es Zurdo?</label
							>
						</div>
						<div class="valid-feedback" id="id_eszurdo_validate">¡Se ve bien!</div>
					</div>
				</div>
				<hr />
				<h3 class="fw-bold text-primary">Archivos</h3>
				<div class="row g-3">
					<div class="col-md-4">
						<label for="id_documento_archivo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Documento:</label
						>
						{#if ePersona.estadodocumento != 2}
							<FileUploader
								inputID="id_documento_archivo"
								inputName="documento_archivo"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedDocumento}
								on:fileRemoved={handleFileRemovedDocumento}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
						{/if}
						{#if ePersona.download_documento != ''}
							<div class="fs-6">
								Tienes un archivo subido:
								<a
									title="Ver archivo"
									href={ePersona.download_documento}
									target="_blank"
									class="text-primary text-center">Ver archivo</a
								>
							</div>
						{/if}

						<div class="valid-feedback" id="id_documento_archivo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4">
						<label for="id_papeleta_archivo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Papeleta de votación:</label
						>
						{#if ePersona.estadopapeleta != 2}
							<FileUploader
								inputID="id_papeleta_archivo"
								inputName="papeleta_archivo"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedPapeleta}
								on:fileRemoved={handleFileRemovedPapeleta}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
						{/if}
						{#if ePersona.download_papeleta != ''}
							<div class="fs-6">
								Tienes un archivo subido:
								<a
									title="Ver archivo"
									href={ePersona.download_papeleta}
									target="_blank"
									class="text-primary text-center">Ver archivo</a
								>
							</div>
						{/if}

						<div class="valid-feedback" id="id_papeleta_archivo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-4">
						<label for="id_libretamilitar_archivo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Libreta militar:</label
						>
						{#if ePersona.estadolibretamilitar != 2}
							<FileUploader
								inputID="id_libretamilitar_archivo"
								inputName="libretamilitar_archivo"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedLibretaMilitar}
								on:fileRemoved={handleFileRemovedLibretaMilitar}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
						{/if}
						{#if ePersona.download_libretamilitar != ''}
							<div class="fs-6">
								Tienes un archivo subido:
								<a
									title="Ver archivo"
									href={ePersona.download_libretamilitar}
									target="_blank"
									class="text-primary text-center">Ver archivo</a
								>
							</div>
						{/if}

						<div class="valid-feedback" id="id_libretamilitar_archivo_validate">¡Se ve bien!</div>
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
			<Button color="secondary" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
			{#if !load}
				<Button color="primary" class="rounded-3 btn-sm" on:click={saveDatosPersonales}
					>Guardar</Button
				>
			{/if}
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
