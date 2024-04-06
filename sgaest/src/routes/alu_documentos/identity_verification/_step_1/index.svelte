<script lang="ts">
	import { apiPOST, apiPOSTFormData, browserGet } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	export let eMatriculaSedeExamen;
	let hasBeenAdded = false;
	let inputUtilizarArchivo = false;
	const dispatch = createEventDispatcher();
	let fileDocumentoIdentidad;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		await delay(2000);
	});

	const handleFileSelectedDocumentoIdentidad = (event) => {
		fileDocumentoIdentidad = event.detail;
		hasBeenAdded = true;
	};

	const handleFileRemovedDocumentoIdentidad = () => {
		fileDocumentoIdentidad = null;
		hasBeenAdded = false;
	};

	const handleSubmit = async () => {
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
				dispatch('actionRun', {
					action: 'changeStep',
					next: 2,
					previous: 1,
					aData: {
						//fileDocumentoIdentidad: fileDocumentoIdentidad.file ?? undefined
						eMatriculaSedeExamen: res.data['eMatriculaSedeExamen']
					}
				});
				return;
			}
		}

		return;
	};
</script>

<svelte:head>
	<title>Verificación de identidad | Documento de identidad</title>
</svelte:head>
<form id="frmDocumentoIdentidad" on:submit|preventDefault={handleSubmit}>
	<div class="bg-light card shadow-none border-0 px-lg-12 mt-2">
		<div class="bg-light card-header border-0 px-4 py-3 pt-5">
			<h3 class="mb-0 card-title fw-bold text-center">
				<span class="px-6 text-warning">Documento de identidad</span>
			</h3>
			<p class="text-center">Cédula, Pasaporte o DNI</p>
		</div>
		{#if eMatriculaSedeExamen.download_archivoidentidad}
			<div class="card-body border-0 mb-1 pb-0">
				<div class="align-items-center" role="alert">
					<p class="m-0 p-0 text-primary">
						<b>IMPORTANTE:</b> Si ya tienes subido el documento de identidad y no deseas actualizarlo
						presiona continuar, caso contrario puedes subir el archivo en formato PDF.
					</p>
				</div>
			</div>
			<div class="card-body border-0 mb-0 py-0">
				<div class="align-items-center text-center">
					<div class="fs-6">
						Tienes un archivo subido:
						<a
							title="Ver archivo"
							href={eMatriculaSedeExamen.download_archivoidentidad}
							target="_blank"
							class="text-danger fw-bold text-center pulso">Ver documento de identidad</a
						>
					</div>
				</div>
			</div>
		{/if}
		<div class="card-body border-0 mt-0 py-3">
			<div class="row g-2">
				<div class="col-md-12 col-lg-12 col-sm-12">
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

					<div class="valid-feedback" id="id_archivoidentidad_validate">¡Se ve bien!</div>
				</div>
				{#if hasBeenAdded}
					<div class="col-md-12 col-lg-12 col-sm-12">
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
				{/if}
			</div>
		</div>

		<div class="bg-light card-footer border-0 p-0 py-5">
			<!--<p class="text-center mt-5">
				Los campos (<span class="fw-bold text-warning">*</span>) son obligatorios para continuar con
				el proceso de inscripción.
			</p>-->
			<div class="d-flex justify-content-center gap-4">
				<button
					type="button"
					class="btn btn-warning rounded-pill text-white px-lg-8 px-xl-8 px-md-8 px-sm-6"
					on:click={() => goto('/alu_documentos')}>Cancelar</button
				>
				<button
					type="submit"
					id="btnContinuar"
					class="btn btn-primary rounded-pill px-lg-8 px-xl-8 px-md-8 px-sm-6">Continuar</button
				>
			</div>
		</div>
	</div>
</form>

<style>
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
