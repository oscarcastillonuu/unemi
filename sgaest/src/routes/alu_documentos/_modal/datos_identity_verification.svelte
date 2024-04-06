<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { Spinner } from 'sveltestrap';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import Iframe from '$components/Iframe.svelte';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import FilePondPluginImageValidateSize from 'filepond-plugin-image-validate-size';
	import FilePondPluginImageCrop from 'filepond-plugin-image-crop';
	import FilePondPluginImageResize from 'filepond-plugin-image-resize';
	import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation';
	import FilePondPluginImageEdit from 'filepond-plugin-image-edit';
	import FilePondPluginImagePreview from 'filepond-plugin-image-preview';
	import FilePondPluginImageTransform from 'filepond-plugin-image-transform';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { goto } from '$app/navigation';
	import { apiPOSTFormData, changeProfile } from '$lib/utils/requestUtils';
	const dispatch = createEventDispatcher();

	export let aData;
	let eMatriculaSedeExamen = undefined;
	let load = true;
	let nameFoto = 'fileFoto';
	let editarFoto = false;
	let editarDocumento = false;
	let hasBeenAdded = false;
	let inputCambiarFoto = false;
	let inputUtilizarArchivo = false;
	let pondFoto;
	let fileDocumentoIdentidad;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		registerPlugin(
			FilePondPluginFileValidateType,
			FilePondPluginImageValidateSize,
			FilePondPluginImageCrop,
			FilePondPluginImageResize,
			FilePondPluginImageExifOrientation,
			FilePondPluginImageEdit,
			FilePondPluginImagePreview,
			FilePondPluginImageTransform
		);
		eMatriculaSedeExamen = aData ?? undefined;
		console.log('eMatriculaSedeExamen: ', eMatriculaSedeExamen);
		await delay(2000);
		load = false;
	});
	const handleInit = () => {
		console.log('FilePond has initialised');
	};
	const handleOnaddfilestart = (file) => {
		console.log(file);
		loading.setLoading(true, 'Procesando el archivo, espere por favor...');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondFoto.getFiles());
		console.log('A file has been added', fileItem);
		hasBeenAdded = true;
		loading.setLoading(false, 'Procesando el archivo, espere por favor...');
	};

	const handleOnRemoveFile = (error, file) => {
		hasBeenAdded = false;
	};

	const handleFileSelectedDocumentoIdentidad = (event) => {
		fileDocumentoIdentidad = event.detail;
		hasBeenAdded = true;
	};

	const handleFileRemovedDocumentoIdentidad = () => {
		fileDocumentoIdentidad = null;
		hasBeenAdded = false;
	};

	const actionSaveFotoPerfil = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmFotoPerfil = document.getElementById('frmFotoPerfil');
		const formData = new FormData($frmFotoPerfil);
		let efileFoto = undefined;
		if (pondFoto && pondFoto.getFiles().length > 0) {
			efileFoto = pondFoto.getFiles()[0];
			formData.append('archivofoto', efileFoto.file);
		}
		formData.append('utilizarfoto', inputCambiarFoto ? 'true' : 'false');
		formData.append('action', 'saveMatriculaSedeExamenFotoPerfil');
		console.log('formData: ', formData);
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/aulavirtual', formData);
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
				return;
			} else {
				loading.setLoading(true, 'Cargando, espere por favor...');
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				if (inputCambiarFoto) {
					await delay(2000);
					await changeProfile('token/change/profile', {}, 3);
				} else {
					//goto('/alu_documentos');
					eMatriculaSedeExamen = { ...res.data.eMatriculaSedeExamen };
					dispatch('actionRun', {
						action: 'changeMatriculaExamenSede',
						eMatriculaSedeExamen: { ...eMatriculaSedeExamen }
					});
					editarFoto = false;
					pondFoto = undefined;
					hasBeenAdded = false;
					inputCambiarFoto = false;
					loading.setLoading(false, 'Cargando, espere por favor...');
				}

				return;
			}
		}

		return;
	};

	const actionSaveDocumentoIdentidad = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDocumentoIdentidad = document.getElementById('frmDocumentoIdentidad');
		const formData = new FormData($frmDocumentoIdentidad);
		if (fileDocumentoIdentidad) {
			formData.append('archivoidentidad', fileDocumentoIdentidad.file);
		}
		formData.append('utilizararchivo', inputUtilizarArchivo ? 'true' : 'false');

		formData.append('action', 'saveMatriculaSedeExamenDocumentoIdentidad');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/aulavirtual', formData);
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
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				//goto('/alu_documentos');
				eMatriculaSedeExamen = { ...res.data.eMatriculaSedeExamen };
				dispatch('actionRun', {
					action: 'changeMatriculaExamenSede',
					eMatriculaSedeExamen: { ...eMatriculaSedeExamen }
				});
				editarDocumento = false;
				fileDocumentoIdentidad = undefined;
				hasBeenAdded = false;
				inputUtilizarArchivo = false;
				return;
			}
		}

		return;
	};
</script>

{#if !load}
	{#if eMatriculaSedeExamen}
		{#if eMatriculaSedeExamen.tiene_fase_2}
			<div class="alert alert-warning d-flex align-items-center" role="alert">
				<div>
					<h4 class="alert-heading fw-bold">Recuerda</h4>
					Podras cambiar la foto de perfil o el documento de identidad mientras no hayas aceptado el&nbsp;<b
					>
						ACUERDO DE TÉRMINOS Y CONDICIONES PARA RENDIR LOS EXÁMENES</b
					>
				</div>
			</div>
		{/if}
		<div class="row m-0 p-0 ">
			<div class="col-lg-6 col-md-6 col-12 text-center">
				<h3 class="">Foto de perfil</h3>
				{#if editarFoto}
					<form id="frmFotoPerfil" on:submit|preventDefault={actionSaveFotoPerfil}>
						<div class="my-3">
							<button
								class="btn btn-warning rounded-pill text-black px-lg-8 px-xl-8 px-md-8 px-sm-6"
								on:click={() => {
									{
										editarFoto = !editarFoto;
										pondFoto = undefined;
										hasBeenAdded = false;
										inputCambiarFoto = false;
									}
								}}>Cancelar edición foto de perfil</button
							>
						</div>
						<div class="m-sm-1 mx-md-16">
							<FilePond
								class="pb-0 mb-0 filepond"
								style=""
								labelIdle={[
									'Arrastra y suelta tu foto </br> <span class="filepond--label-action">Subir imagen</span>'
								]}
								bind:this={pondFoto}
								{nameFoto}
								allowMultiple={true}
								oninit={handleInit}
								onaddfile={handleAddFile}
								onaddfilestart={handleOnaddfilestart}
								onremovefile={handleOnRemoveFile}
								acceptedFileTypes={['image/png, image/jpeg']}
								stylePanelLayout="compact circle"
								labelInvalidField="El campo contiene archivos no válidos"
								maxFiles="1"
								maxParallelUploads="1"
								imagePreviewHeight="170"
								imageCropAspectRatio="1:1"
								imageResizeTargetWidth="200"
								imageResizeTargetHeight="200"
								styleLoadIndicatorPosition="center bottom"
								styleProgressIndicatorPosition="center bottom"
								styleButtonRemoveItemPosition="center bottom"
								styleButtonProcessItemPosition="center bottom"
							/>
							<small class="text-primary">Tamaño máximo permitido 15Mb, en formato jpg</small>
						</div>
						{#if hasBeenAdded}
							<div class="mt-4">
								<div class="form-check form-switch">
									<input
										class="form-check-input"
										type="checkbox"
										id="id_cambiofoto"
										bind:checked={inputCambiarFoto}
									/>
									<label class="form-check-label fw-bold text-dark" for="id_cambiofoto"
										>¿Desea utilizar la foto como foto de perfil?</label
									>
								</div>
							</div>
							<div class="mt-4">
								<button
									type="submit"
									class="btn btn-success rounded-pill px-lg-8 px-xl-8 px-md-8 px-sm-6"
									>Guardar</button
								>
							</div>
						{/if}
						<div class="ps-lg-7">
							<!--<span
							class=" text-primary ls-md text-uppercase
                      fw-semi-bold">Build fast, launch faster</span
						>-->
							<h2 class="display-6 mt-4 mb-3 fw-bold">Términos y condiciones</h2>
							<!--<h3>
							Mauris interdum leo vel eleifend fringilla nibh elit interdc nunc elementum nisi.
						</h3>-->
							<div class="m-0 ">
								<ul class="list-unstyled mb-0 fs-6">
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> La fotografía debe ser tomada en plano
										medio corto (medio cuerpo, del pecho hacia arriba).
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> La fotografía debe ser cuadrada.
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> En la fotografía, procure proyectar
										un aspecto profesional.
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> Procure, en lo posible, que el fondo
										sea claro (se recomienda color blanco).
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> Está permitido sonreír.
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> La fotografía debe ser actual.
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> Procure subir una fotografía nítida,
										con la mejor resolución posible.
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> La foto tiene que ser a color.
									</li>
									<li class="mb-1 d-flex align-items-center">
										<i class="fe fe-check  text-success me-2" /> Evite utilizar filtros o efectos artísticos.
									</li>
								</ul>
							</div>
						</div>
					</form>
				{:else}
					{#if !eMatriculaSedeExamen.tiene_fase_2}
						<div class="my-3">
							<button
								class="btn btn-danger rounded-pill text-white px-lg-8 px-xl-8 px-md-8 px-sm-6"
								on:click={() => (editarFoto = !editarFoto)}>Cambiar foto de perfil</button
							>
						</div>
					{/if}
					<div>
						<img
							class="rounded-circle"
							src={eMatriculaSedeExamen.download_archivofoto}
							width="250"
							height="250"
						/>
					</div>
				{/if}
			</div>
			<div class="col-lg-6 col-md-6 col-12 text-center">
				<h3>Documento de identidad</h3>
				{#if editarDocumento}
					<form id="frmDocumentoIdentidad" on:submit|preventDefault={actionSaveDocumentoIdentidad}>
						<div class="my-3">
							<button
								class="btn btn-warning rounded-pill text-black px-lg-8 px-xl-8 px-md-8 px-sm-6"
								on:click={() => {
									{
										editarDocumento = !editarDocumento;
										fileDocumentoIdentidad = undefined;
										hasBeenAdded = false;
										inputUtilizarArchivo = false;
									}
								}}>Cancelar edición documento identidad</button
							>
						</div>
						<div class="m-sm-1 mx-md-16">
							<FileUploader
								inputID="id_archivoidentidad"
								inputName="archivoidentidad"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedDocumentoIdentidad}
								on:fileRemoved={handleFileRemovedDocumentoIdentidad}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
						</div>
						{#if hasBeenAdded}
							<div class="text-center">
								<div class="form-check form-switch">
									<input
										class="form-check-input"
										type="checkbox"
										id="id_utlizararchivo"
										bind:checked={inputUtilizarArchivo}
									/>
									<label class="form-check-label fw-bold text-dark" for="id_utlizararchivo"
										>¿Desea utilizar el archivo para la hoja de vida?</label
									>
								</div>
							</div>
							<div class="mt-4">
								<button
									type="submit"
									class="btn btn-success rounded-pill px-lg-8 px-xl-8 px-md-8 px-sm-6"
									>Guardar</button
								>
							</div>
						{/if}
					</form>
				{:else}
					{#if !eMatriculaSedeExamen.tiene_fase_2}
						<div class="my-3">
							<button
								class="btn btn-danger rounded-pill text-white px-lg-8 px-xl-8 px-md-8 px-sm-6"
								on:click={() => (editarDocumento = !editarDocumento)}
								>Cambiar documento de identidad</button
							>
						</div>
					{/if}
					<div class="vh-100">
						<Iframe app="documento" url={eMatriculaSedeExamen.download_archivoidentidad} />
					</div>
				{/if}
			</div>
		</div>
	{/if}
{:else}
	<div class="row justify-content-center align-items-center p-5 m-0">
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}

<style global>
	@import 'filepond/dist/filepond.css';
	@import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css';
	@import 'filepond-plugin-image-edit/dist/filepond-plugin-image-edit.css';
	.filepond--drop-label {
		border-radius: 0.75rem;
		color: #ffffff;
		background: #335f7f !important;
		box-shadow: 0 0.1875rem 0.625rem rgb(0 0 0 / 15%) !important;
	}
</style>
