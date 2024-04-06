<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	import { getInstitucionesBecas as loadDataInstitucionBeca } from '$lib/utils/loadDataApi';
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	let eBeca;
	const dispatch = createEventDispatcher();
	const flatpickrFechaInicioOptions = {
		element: '#id_fechainicio_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaFinOptions = {
		element: '#id_fechafin_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputFechaInicio = '';
	let inputFechaFin = '';
	let inputVerificado = false;
	let selectTipoInstitucion = 0;
	let readSelectionInstitucion;
	let selectionInstitucion;
	let eTipos = [
		//{ id: 0, name: '--Seleccione--' },
		{ id: 1, name: 'PÚBLICA' },
		{ id: 2, name: 'PRIVADA' },
		{ id: 3, name: 'MIXTA' }
	];
	let download_archivo = '';
	let fileArchivo;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eBeca = aData.eBeca;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eBeca) {
			inputVerificado = eBeca.verificado ?? false;
			inputFechaInicio = eBeca.fechainicio ?? '';
			inputFechaFin = eBeca.fechafin ?? '';
			if (eBeca.institucion) {
				selectionInstitucion = eBeca.institucion['pk'] ?? null;
				readSelectionInstitucion = {
					id: eBeca.institucion['pk'],
					name: eBeca.institucion['nombre']
				};
			}
			selectTipoInstitucion = eBeca.tipoinstitucion ?? 0;
			if (eBeca.download_archivo) {
				download_archivo = eBeca.download_archivo;
			}
		}

		await delay(2000);
		load = false;
	});

	const saveFormacionAcademicaBecaExterna = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatoBecaExterna = document.getElementById('frmDatoBecaExterna');
		const formData = new FormData($frmDatoBecaExterna);

		formData.append('tipoinstitucion', selectTipoInstitucion.toString());
		const fechainicio = document.getElementById('id_fechainicio');
		const fechafin = document.getElementById('id_fechafin');
		if (readSelectionInstitucion != null) {
			formData.append('institucion', readSelectionInstitucion.id);
		}
		if (fechainicio) {
			formData.append('fechainicio', fechainicio.value);
		}
		if (fechafin) {
			formData.append('fechafin', fechafin.value);
		}
		if (fileArchivo) {
			formData.append('archivo', fileArchivo.file);
		}
		if (eBeca != undefined) {
			formData.append('id', eBeca.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('action', 'saveFormacionAcademicaBecaExterna');
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
				dispatch('actionRun', { action: 'saveFormacionAcademicaBecaExterna' });
			}
		}
	};

	const handleFileSelectedArchivo = (event) => {
		fileArchivo = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileArchivo = null;
	};
	const changeInstitucion = (event) => {};
</script>

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
			<form action="javascript:;" id="frmDatoBecaExterna">
				<div class="row g-3">
					<div class="col-12">
						<label for="id_tipoinstitucion" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Tipo Institución
						</label>
						<select
							class="form-select form-select-sm"
							aria-label=""
							id="id_tipoinstitucion"
							bind:value={selectTipoInstitucion}
						>
							<option value={0} selected> ----------- </option>
							{#each eTipos as eTipo}
								{#if selectTipoInstitucion === eTipo.id}
									<option value={eTipo.id} selected>
										{eTipo.name}
									</option>
								{:else}
									<option value={eTipo.id}>
										{eTipo.name}
									</option>
								{/if}
							{/each}
						</select>
						<div class="valid-feedback" id="id_tipoinstitucion_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<label for="id_institucion" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Institución:</label
						>
						<FormSelectSearch
							inputId="id_institucion"
							name="institucion"
							minQuery={1}
							bind:value={readSelectionInstitucion}
							on:actionChangeSelectSearch={changeInstitucion}
							fetch={(query) => loadDataInstitucionBeca(query)}
						/>
						<div class="valid-feedback" id="id_institucion_validate">¡Se ve bien!</div>
					</div>

					<div class="col-md-6 col-12">
						<label for="id_fechainicio" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha inicio:</label
						>
						<Flatpickr
							options={flatpickrFechaInicioOptions}
							bind:value={inputFechaInicio}
							element="#id_fechainicio_element"
						>
							<div class="flatpickr input-group" id="id_fechainicio_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechainicio"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechainicio_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_fechafin" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha fin:</label
						>
						<Flatpickr
							options={flatpickrFechaFinOptions}
							bind:value={inputFechaFin}
							element="#id_fechafin_element"
						>
							<div class="flatpickr input-group" id="id_fechafin_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechafin"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechafin_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<label for="id_archivo" class="form-label fw-bold">Certificado:</label>
						<FileUploader
							inputID="id_archivo"
							inputName="archivo"
							acceptedFileTypes={['application/pdf']}
							labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
							on:fileSelected={handleFileSelectedArchivo}
							on:fileRemoved={handleFileRemovedArchivo}
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
			<Button color="warning" class="rounded-5 btn-sm" on:click={saveFormacionAcademicaBecaExterna}
				><i class="fe fe-check" /> Guardar</Button
			>
		{/if}
		<Button color="secondary" class="rounded-5 btn-sm " on:click={mToggle}
			><i class="fe fe-x" /> Cancelar</Button
		>
	</ModalFooter>
</Modal>

<style>
	.form-select {
		border-color: #aaa;
	}
	.form-control {
		border-color: #aaa;
	}
</style>
