<script lang="ts">
	import Swal from 'sweetalert2';
	import { goto } from '$app/navigation';
	import { addToast } from '$lib/store/toastStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { addNotification } from '$lib/store/notificationStore';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	export let aDataModalArchivo;
	let observacion;
	let selectedOption;
	let pondDocumento;
	let nameDocumento = 'fileDocumento';
	let idcerti;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		idcerti = aDataModalArchivo.idcerti;
		//		console.log(eCerti.id);
		registerPlugin(FilePondPluginFileValidateType);
	});

	const dispatch = createEventDispatcher();
	const closeModalArchivo = () => {
		dispatch('actionRun', {
			action: 'closeModalSubir'
		});
	};
	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondDocumento.getFiles());
		console.log('A file has been added', fileItem);
	};

	const limpiarcampos = () => {
		observacion = '';
	};

	const saveInfoArchivo = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoArchivo = document.querySelector('#frmInfoArchivo');
		const formData = new FormData($frmInfoArchivo);

		formData.append('action', 'addRequest');
		formData.append('observacion', observacion);
		formData.append('product', 'certificado');
		formData.append('aData', JSON.stringify(aDataModalArchivo.eCertificado));

		let fileDocumento = pondDocumento.getFiles();
		if (fileDocumento.length == 0) {
			addNotification({
				msg: 'Debe subir un archivo',
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

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/secretary/solicitud', formData);

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
				closeModalArchivo();
				limpiarcampos();
				alertsucess()
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const saveInfoArchivo2 = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoArchivo = document.querySelector('#frmInfoArchivo');
		const formData = new FormData($frmInfoArchivo);

		formData.append('action', 'addRequest');
		formData.append('observacion', observacion);
		formData.append('product', 'certificado');
		formData.append('aData', JSON.stringify(aDataModalArchivo.eCertificado));

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/secretary/solicitud', formData);

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
				closeModalArchivo();
				limpiarcampos();
				alertsucess()
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};

	const alertsucess = async () => {
		const mensajeOtro = {
			title: `NOTIFICACIÓN`,
			html: `Su solicitud de <b>Certificado Personalizado</b> ha sido emitida correctamente`,
			type: 'info',
			icon: 'info',
			showCancelButton: true,
			showConfirmButton: false,
			allowOutsideClick: false,
			cancelButtonColor: '#0d6efd',
			cancelButtonText: 'Ir a mis pedidos'
		};
		Swal.fire(mensajeOtro).then(async (result) => {
			if (result.value) {
				addToast({
					type: 'info',
					header: 'Información',
					body: 'Puede seguir agregando o descargando mas certificados'
				});
			} else {
				goto('/alu_secretaria/mis_pedidos');
			}
		});
	};
</script>

{#if idcerti == 58 || idcerti == 59}
	<form enctype="multipart/form-data" id="frmInfoArchivo" on:submit|preventDefault={saveInfoArchivo2}>
		<div class="card-body">
			<div class="alert alert-warning alert-dismissible">
				En el apartado de observación, detallar el contenido de su certificado personalizado.<br />
			</div>

			<div class="row g-3 mb-5">
				<div class="col-md-12">
					<label for="ePersonaObservacion" class="form-label fw-bold"
						><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" /> Observación:</label
					>
					<textarea
						rows="3"
						cols="100"
						type="text"
						class="form-control"
						id="eObservacion"
						bind:value={observacion}
						required
					/>
				</div>
			</div>

			<div class="row g-3">
				<div class="col-md-3">
					<label for="eOpcion1" class="form-label fw-bold">
						<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" /> Documento físico: </label>
					<input type="radio" id="opcion1" name="opciones" value="opcion1" on:change={selectedOption}/>
				</div>
				<div class="col-md-5">
					<label for="eOpcion2" class="form-label fw-bold">
						<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" /> Documento con firma electrónica:</label>
					<input type="radio" id="opcion2" name="opciones" value="opcion2" on:change={selectedOption}/>
				</div>
			</div>

			<div class="card-footer text-muted">
				<div class="d-grid gap-2 d-md-flex justify-content-md-end">
					<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
					<button type="submit" class="btn btn-info">Guardar</button>
					<a color="danger" class="btn btn-danger" on:click={() => closeModalArchivo()}>Cerrar</a>
				</div>
			</div>
		</div>
	</form>
{:else}
	<form enctype="multipart/form-data" id="frmInfoArchivo" on:submit|preventDefault={saveInfoArchivo}>
		<div class="card-body">
			<div class="alert alert-warning alert-dismissible">
				{#if idcerti == 55}
					En el formato encontrará un ejemplo que debe seguirse para realizar correctamente la
					solicitud del certificado personalizado.<br />
					Recuerde que los certificados personalizados son digitales, lo que significa que los usuarios
					deben descargarlos desde el sistema en lugar de venir a retirarlos físicamente.
					<b>
						<a
							href="{variables.BASE_API_STATIC}/formatos/solicitud_para_certificados_academicos_personalizados.docx"
							target="_blank"
							><i class="bi bi-download" />
							Descargar Formato</a
						>
					</b>
				{:else}
					En el formato encontrará un ejemplo que debe seguirse para realizar correctamente la
					solicitud del certificado físico.<br />
					Recuerde que estos certificados físicos solo aplican para apostillas, concursos de méritos y
					ascensos.<br />
					<b>
						<a
							href="{variables.BASE_API_STATIC}/formatos/solicitud_para_certificados_academicos_fisicos.docx"
							target="_blank"
							><i class="bi bi-download" />
							Descargar Formato</a
						>
					</b>
				{/if}
			</div>

			<div class="row g-3">
				<div class="col-md-12">
					<label for="ePersonaObservacion" class="form-label fw-bold"
						><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" /> Observación:</label
					>
					<textarea
						rows="3"
						cols="100"
						type="text"
						class="form-control"
						id="eObservacion"
						bind:value={observacion}
					/>
				</div>
				<div class="col-md-12">
					<label for="ePersonaFileDocumento" class="form-label fw-bold">
						<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" /> Archivo:</label
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
			</div>
			<div class="card-footer text-muted">
				<div class="d-grid gap-2 d-md-flex justify-content-md-end">
					<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
					<button type="submit" class="btn btn-info">Guardar</button>
					<a color="danger" class="btn btn-danger" on:click={() => closeModalArchivo()}>Cerrar</a>
				</div>
			</div>
		</div>
	</form>
{/if}

<style global>
	@import 'filepond/dist/filepond.css';
</style>
