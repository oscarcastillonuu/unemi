<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	import {
		getRazas as loadRazas,
		getNacionalidadesIndigenas as loadNacionalidades
	} from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import FormSelect from '$components/Formulario/Select.svelte';
	import FormMultiselect from '$components/Formulario/Multiselect.svelte';
	export let aData;
	export let mToggle;
	let ePerfilInscripcion;
	let eRazas;
	let eNacionalidades;
	const dispatch = createEventDispatcher();
	const flatpickrOptions = {
		element: '#id_nacimiento_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let selectRaza = 0;
	let selectNacionalidad = 0;
	let fileRaza;
	let download_archivo = '';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePerfilInscripcion = aData.ePerfilInscripcion;
		mensaje_load = 'Consultado la información, espere por favor...';
		eNacionalidades = await loadNacionalidades();
		eRazas = await loadRazas();
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (ePerfilInscripcion.raza) {
			selectRaza = ePerfilInscripcion.raza['pk'] ?? 0;
		}
		if (ePerfilInscripcion.nacionalidadindigena) {
			selectNacionalidad = ePerfilInscripcion.nacionalidadindigena['pk'] ?? 0;
		}
		if (ePerfilInscripcion.download_archivoraza) {
			download_archivo = ePerfilInscripcion.download_archivoraza;
		}

		await delay(2000);
		load = false;
	});

	const saveDatosPersonalesEtnia = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmEtnia = document.getElementById('frmEtnia');
		const formData = new FormData($frmEtnia);
		//const numeros = /^([0-9])*$/;
		if (selectRaza != 0) {
			formData.append('raza', selectRaza.toString());
		}

		if (selectNacionalidad != 0) {
			formData.append('nacionalidadindigena', selectNacionalidad.toString());
		}

		if (fileRaza) {
			formData.append('archivoraza', fileRaza.file);
		}
		formData.append('action', 'saveDatosPersonalesEtnia');
		//console.log(selectDiscapacidadMultiples);
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
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
				dispatch('actionRun', { action: 'saveDatosPersonalesEtnia' });
			}
		}
	};

	const handleFileSelectedEtnia = (event) => {
		fileRaza = event.detail;
	};

	const handleFileRemovedEtnia = () => {
		fileRaza = null;
	};
</script>

{#if ePerfilInscripcion}
	<Modal
		id="modal_edit_etnia"
		isOpen={true}
		toggle={mToggle}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">Editar datos de étnia, pueblo y nacionalidad</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmEtnia">
					<div class="row g-3">
						<div class="col-md-12 col-lg-12 col-sm-12">
							<label for="id_raza" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Étnia:</label
							>
							{#if eRazas.length > 0}
								<select
									class="form-select form-select-sm"
									aria-label=""
									required
									id="id_raza"
									bind:value={selectRaza}
								>
									{#each eRazas as eRaza}
										{#if selectRaza === eRaza.id}
											<option value={eRaza.id} selected>
												{eRaza.name}
											</option>
										{:else}
											<option value={eRaza.id}>
												{eRaza.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_raza_validate">¡Se ve bien!</div>
						</div>
						{#if selectRaza === 1}
							<div class="col-md-12 col-lg-12 col-sm-12">
								<label for="id_nacionalidadindigena" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Nacionalidad indigena:</label
								>
								{#if eNacionalidades.length > 0}
									<select
										class="form-select form-select-sm"
										aria-label=""
										required
										id="id_nacionalidadindigena"
										bind:value={selectNacionalidad}
									>
										{#each eNacionalidades as eNacionalidad}
											{#if selectNacionalidad === eNacionalidad.id}
												<option value={eNacionalidad.id} selected>
													{eNacionalidad.name}
												</option>
											{:else}
												<option value={eNacionalidad.id}>
													{eNacionalidad.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
								<div class="valid-feedback" id="id_nacionalidadindigena_validate">¡Se ve bien!</div>
							</div>
						{/if}
						<div class="col-md-12 col-lg-12 col-sm-12">
							<label for="id_archivo" class="form-label fw-bold">Archivo del carné:</label>
							<FileUploader
								inputID="id_archivoraza"
								inputName="archivoraza"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedEtnia}
								on:fileRemoved={handleFileRemovedEtnia}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
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
							{/if}

							<div class="valid-feedback" id="id_archivoraza_validate">¡Se ve bien!</div>
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
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosPersonalesEtnia}
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
