<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { getEnfermedades as loadDataEnfermedades } from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';

	export let aData;
	export let mToggle;
	export let mTitle;
	let ePersonaEnfermedad;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let readSelectionEnfermedad;
	let fileValoracion;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePersonaEnfermedad = aData.ePersonaEnfermedad ?? {};
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (ePersonaEnfermedad != undefined) {
			const enfermedad = ePersonaEnfermedad.enfermedad;
			if (enfermedad) {
				readSelectionEnfermedad = {
					id: enfermedad['pk'],
					name: enfermedad['descripcion']
				};
			}
		}
		await delay(2000);
		load = false;
	});

	const saveDatosMedicoEnfermedad = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmEnfermedad = document.getElementById('frmEnfermedad');
		const formData = new FormData($frmEnfermedad);
		if (ePersonaEnfermedad != undefined) {
			formData.append('id', ePersonaEnfermedad.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		if (readSelectionEnfermedad != null) {
			formData.append('enfermedad', readSelectionEnfermedad.id);
		}
		if (fileValoracion) {
			formData.append('archivomedico', fileValoracion.file);
		}

		formData.append('action', 'saveDatosMedicoEnfermedad');
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
				dispatch('actionRun', { action: 'saveDatosPersonalesMedico' });
			}
		}
	};

	const handleFileSelectedArchivo = (event) => {
		fileValoracion = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileValoracion = null;
	};

	const changeEnfermedad = (event) => {};
</script>

{#if ePersonaEnfermedad}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmEnfermedad">
					<div class="row g-3">
						<div class="col-12">
							<label for="id_enfermedad" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Enfermedad:</label
							>
							<FormSelectSearch
								inputId="id_enfermedad"
								name="enfermedad"
								bind:value={readSelectionEnfermedad}
								on:actionChangeSelectSearch={changeEnfermedad}
								fetch={(query) => loadDataEnfermedades(query)}
							/>
							<div class="valid-feedback" id="id_enfermedad_validate">¡Se ve bien!</div>
						</div>
					</div>
					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-12">
							<label for="id_archivomedico" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Valoración médica:</label
							>
							{#if ePersonaEnfermedad.estadoarchivo != 2}
								<FileUploader
									inputID="id_archivomedico"
									inputName="archivomedico"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedArchivo}
									on:fileRemoved={handleFileRemovedArchivo}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if ePersonaEnfermedad.download_archivomedico}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={ePersonaEnfermedad.download_archivomedico}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivomedico_validate">¡Se ve bien!</div>
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
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosMedicoEnfermedad}
					><i class="fe fe-check" /> Guardar</Button
				>
			{/if}
			<Button color="secondary" class="rounded-5 btn-sm " on:click={mToggle}
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
