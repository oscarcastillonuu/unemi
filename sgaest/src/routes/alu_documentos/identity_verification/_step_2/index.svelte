<script lang="ts">
	import { apiPOSTFormData, changeProfile } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
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
	const dispatch = createEventDispatcher();
	export let eMatriculaSedeExamen;
	let nameFoto = 'fileFoto';
	let hasBeenAdded = false;
	let inputCambiarFoto = false;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let pondFoto;
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
		await delay(2000);
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

	const handleSubmit = async () => {
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
					goto('/alu_documentos');
				}
				return;
			}
		}

		return;
	};
</script>

<svelte:head>
	<title>Verificación de identidad | Foto de perfil</title>
</svelte:head>
<form id="frmFotoPerfil" on:submit|preventDefault={handleSubmit}>
	<div class="bg-light card shadow-none border-0 px-lg-2 mt-2">
		<div class="bg-light card-header border-0 px-4 py-3">
			<h3 class="mb-0 card-title fw-bold text-center">
				<span class="px-6 text-warning">Foto de perfil</span>
			</h3>
		</div>
		{#if eMatriculaSedeExamen.download_archivofoto}
			<div class="card-body border-0 mb-1 pb-0">
				<div class="align-items-center" role="alert">
					<p class="m-0 p-0 text-primary">
						<b>IMPORTANTE:</b> Si ya tienes subido la foto de perfil y no deseas actualizarla presiona
						finalizar, caso contrario puedes subir el archivo en formato jpg.
					</p>
				</div>
			</div>
		{/if}
		<div class="card-body border-0 mt-0 py-3">
			<div class="row align-items-center">
				<div class="col-lg-4 col-md-12 col-12">
					<!-- image -->
					<div class="mb-4 mb-lg-0 text-center">
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
					{/if}
					{#if eMatriculaSedeExamen.download_archivofoto}
						<div class="fs-6">
							Tienes una foto de perfil:
							<a
								title="Ver archivo"
								href={eMatriculaSedeExamen.download_archivofoto}
								target="_blank"
								class="text-danger fw-bold pulso text-center">Ver foto de perfil</a
							>
						</div>
					{/if}
				</div>
				<div class="col-lg-8 col-md-12 col-12 m-0">
					<!-- content -->
					<div class="ps-lg-7">
						<!--<span
							class=" text-primary ls-md text-uppercase
                      fw-semi-bold">Build fast, launch faster</span
						>-->
						<h2 class="display-5 mt-4 mb-3 fw-bold">Términos y condiciones</h2>
						<!--<h3>
							Mauris interdum leo vel eleifend fringilla nibh elit interdc nunc elementum nisi.
						</h3>-->
						<div class="m-0 ">
							<ul class="list-unstyled mb-0">
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La fotografía debe ser tomada en plano
									medio corto (medio cuerpo, del pecho hacia arriba).
								</li>
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La fotografía debe ser cuadrada.
								</li>
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> En la fotografía, procure proyectar un
									aspecto profesional.
								</li>
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Procure, en lo posible, que el fondo sea
									claro (se recomienda color blanco).
								</li>
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Está permitido sonreír.
								</li>
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La fotografía debe ser actual.
								</li>
								<li class="mb-1 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Procure subir una fotografía nítida, con
									la mejor resolución posible.
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
				</div>
			</div>
		</div>

		<div class="bg-light card-footer border-0 p-0 py-5">
			<div class="d-flex justify-content-center gap-4">
				<button
					type="button"
					class="btn btn-warning rounded-pill text-white px-lg-8 px-xl-8 px-md-8 px-sm-6"
					on:click={() => goto('/alu_documentos')}>Cancelar</button
				>
				<button
					type="submit"
					id="btnFinalizar"
					class="btn btn-primary rounded-pill px-lg-8 px-xl-8 px-md-8 px-sm-6">Finalizar</button
				>
			</div>
		</div>
	</div>
</form>

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

	@keyframes latidos {
		from {
			transform: none;
		}
		50% {
			transform: scale(1.4);
		}
		to {
			transform: none;
		}
	}

	.pulso {
		display: inline-block;
		animation: latidos 0.9s infinite;
	}
</style>
