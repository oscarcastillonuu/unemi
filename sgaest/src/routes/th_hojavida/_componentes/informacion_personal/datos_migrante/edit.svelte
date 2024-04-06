<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
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
	import { getPaises as loadPaises } from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import FormSelect from '$components/Formulario/Select.svelte';
	import FormMultiselect from '$components/Formulario/Multiselect.svelte';

	export let aData;
	export let mToggle;
	let eMigrantePersona;
	let readSelectionPais;
	let inputAnioResidencia = 0;
	let inputMesResidencia = 0;
	const dispatch = createEventDispatcher();
	const flatpickrOptions = {
		element: '#id_nacimiento_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let inputFechaRetorno = '';
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let fileDocumento;
	let download_archivo = '';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eMigrantePersona = aData.eMigrantePersona;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eMigrantePersona.paisresidencia) {
			readSelectionPais = {
				id: eMigrantePersona.paisresidencia['pk'],
				name: eMigrantePersona.paisresidencia['nombre']
			};
		}
		if (eMigrantePersona) {
			inputFechaRetorno = eMigrantePersona.fecharetorno ?? '';
			inputAnioResidencia = eMigrantePersona.anioresidencia ?? 0;
			inputMesResidencia = eMigrantePersona.mesresidencia ?? 0;
		}
		await delay(2000);
		load = false;
	});

	const saveDatosPersonalesMigrante = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmMigrante = document.getElementById('frmMigrante');
		const formData = new FormData($frmMigrante);
		if (readSelectionPais != null) {
			formData.append('paisresidencia', readSelectionPais.id);
		}
		const fecha = document.getElementById('id_fecharetorno');
		if (fecha) {
			formData.append('fecharetorno', fecha.value);
		}
		formData.append('anioresidencia', inputAnioResidencia.toString());
		formData.append('mesresidencia', inputMesResidencia.toString());
		formData.append('action', 'saveDatosPersonalesMigrante');
		if (fileDocumento) {
			formData.append('archivo', fileDocumento.file);
		}
		//console.log(selectDiscapacidadMultiples);
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
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
				dispatch('actionRun', { action: 'saveDatosPersonalesMigrante' });
			}
		}
	};

	const changePais = (event) => {};
	const handleFileSelectedDocumento = (event) => {
		fileDocumento = event.detail;
	};

	const handleFileRemovedDocumento = () => {
		fileDocumento = null;
	};
</script>

{#if eMigrantePersona}
	<Modal
		id="modal_edit_etnia"
		isOpen={true}
		toggle={mToggle}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">Editar datos de direccion domiciliaria en el extranjero</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmMigrante">
					<div class="row g-3">
						<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
							<label for="id_paisresidencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> País residencia:</label
							>
							<FormSelectSearch
								inputId="id_paisresidencia"
								name="paisresidencia"
								bind:value={readSelectionPais}
								on:actionChangeSelectSearch={changePais}
								fetch={(query) => loadPaises(query)}
							/>
							<div class="valid-feedback" id="id_paisresidencia_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
							<label for="id_fecharetorno" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha de retorno:</label
							>
							<Flatpickr
								options={flatpickrOptions}
								bind:value={inputFechaRetorno}
								element="#id_fecharetorno_element"
							>
								<div class="flatpickr input-group" id="id_fecharetorno_element">
									<input
										type="text"
										class="form-control form-control-sm"
										placeholder="Seleccione una fecha..."
										data-input
										id="id_fecharetorno"
									/>
									<span class="input-group-text text-muted" title="Fecha" data-toggle
										><i class="fe fe-calendar" /></span
									>
									<span class="input-group-text text-danger" title="clear" data-clear>
										<i class="fe fe-x" />
									</span>
								</div>
							</Flatpickr>
							<div class="valid-feedback" id="id_fecharetorno_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
							<label for="id_anioresidencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Años residencia:</label
							>
							<input
								type="number"
								class="form-control form-control-sm"
								id="id_anioresidencia"
								bind:value={inputAnioResidencia}
							/>
							<div class="valid-feedback" id="id_anioresidencia_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
							<label for="id_mesresidencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Meses residencia:</label
							>
							<input
								type="number"
								class="form-control form-control-sm"
								id="id_mesresidencia"
								bind:value={inputMesResidencia}
							/>
							<div class="valid-feedback" id="id_mesresidencia_validate">¡Se ve bien!</div>
						</div>
					</div>
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-12">
							<label for="id_archivo" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Documento:</label
							>
							{#if eMigrantePersona.estadoarchivo != 2}
								<FileUploader
									inputID="id_archivo"
									inputName="archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedDocumento}
									on:fileRemoved={handleFileRemovedDocumento}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if eMigrantePersona.download_archivo}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={eMigrantePersona.download_archivo}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivo_validate">¡Se ve bien!</div>
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
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosPersonalesMigrante}
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
