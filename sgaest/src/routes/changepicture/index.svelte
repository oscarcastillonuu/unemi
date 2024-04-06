<script lang="ts">
	import {
		apiPOST,
		apiPOSTFormData,
		browserGet,
		changeProfile,
		logOutUser
	} from '$lib/utils/requestUtils';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import FilePondPluginImageValidateSize from 'filepond-plugin-image-validate-size';
	import FilePondPluginImageCrop from 'filepond-plugin-image-crop';
	import FilePondPluginImageResize from 'filepond-plugin-image-resize';
	import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation';
	import FilePondPluginImageEdit from 'filepond-plugin-image-edit';
	import FilePondPluginImagePreview from 'filepond-plugin-image-preview';
	import FilePondPluginImageTransform from 'filepond-plugin-image-transform';
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';
	import { Spinner } from 'sveltestrap';
	import { addNotification } from '$lib/store/notificationStore';
	import { addToast } from '$lib/store/toastStore';
	import { goto } from '$app/navigation';
	const DEBUG = import.meta.env.DEV;
	let Title = 'Cambiar foto de perfil';
	let load = true;
	let itemsBreadCrumb = [{ text: 'Cambiar foto', active: false, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	overrideItemIdKeyNameBeforeInitialisingDndZones('value');
	let pondFoto;
	let nameFoto = 'fileFoto';
	let hasBeenAdded = false;
	onMount(async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
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
		loading.setLoading(false, 'Cargando, espere por favor...');
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

	const uploadPicture = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmPersonaFoto = document.querySelector('#frmPersonaFoto');
		const formData = new FormData($frmPersonaFoto);
		formData.append('action', 'changeProfile');
		let fileFoto = pondFoto.getFiles();
		if (fileFoto.length == 0) {
			addNotification({
				msg: 'Debe subir archivo de documento de cédula o pasaporte',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (fileFoto.length > 1) {
			addNotification({
				msg: 'Archivo de documento debe ser único',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		let efileFoto = undefined;
		if (pondFoto && pondFoto.getFiles().length > 0) {
			efileFoto = pondFoto.getFiles()[0];
		}
		//console.log(efileFoto);
		formData.append('fileFoto', efileFoto.file);
		const [res, errors] = await apiPOSTFormData(fetch, 'changepicture', formData);

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
				// addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				loading.setLoading(false, 'Cargando, espere por favor...');
				//goto('/');
				await changeProfile('token/change/profile', {}, 3);
			}
		}
	};
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>
{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="py-lg-8">
		<div class="container">
			<div class="row align-items-center">
				<div class="col-lg-4 col-md-12 col-12">
					<!-- image -->
					<div class="mb-4 mb-lg-0 text-center">
						<form id="frmPersonaFoto" on:submit|preventDefault={uploadPicture}>
							<FilePond
								class="pb-0 mb-0 filepond"
								style=""
								labelIdle={[
									'Arrastra y suelta tu foto o <span class="filepond--label-action">Subir imagen</span>'
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
							{#if hasBeenAdded}
								<div class="mt-4">
									<button type="submit" class="btn btn-success">Guardar</button>
								</div>
							{/if}
						</form>
					</div>
				</div>
				<div class="col-lg-8 col-md-12 col-12 mt-4 mt-lg-0">
					<!-- content -->
					<div class="ps-lg-7">
						<!--<span
							class=" text-primary ls-md text-uppercase
                      fw-semi-bold">Build fast, launch faster</span
						>-->
						<h2 class="display-4 mt-4 mb-3 fw-bold">Términos y condiciones</h2>
						<!--<h3>
							Mauris interdum leo vel eleifend fringilla nibh elit interdc nunc elementum nisi.
						</h3>-->
						<div class="mt-5 ">
							<ul class="list-unstyled mb-0">
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La fotografía debe ser tomada en plano
									medio corto (medio cuerpo, del pecho hacia arriba).
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La fotografía debe ser cuadrada.
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> En la fotografía, procure proyectar un
									aspecto profesional.
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Procure, en lo posible, que el fondo sea
									claro (se recomienda color blanco).
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Está permitido sonreír.
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La fotografía debe ser actual.
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Procure subir una fotografía nítida, con
									la mejor resolución posible.
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> La foto tiene que ser a color.
								</li>
								<li class="mb-3 d-flex align-items-center">
									<i class="fe fe-check  text-success me-2" /> Evite utilizar filtros o efectos artísticos.
								</li>
							</ul>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
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
