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
	import {
		getDisciplinasDeportivas as loadDataDisciplinas,
		getPaises as loadDataPaises
	} from '$lib/utils/loadDataApi';
	import FormMultiselect from '$components/Formulario/Multiselect.svelte';
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	let eDeportista;
	const dispatch = createEventDispatcher();
	const flatpickrFechaInicioEventoOptions = {
		element: '#id_fechainicioevento_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaFinEventoOptions = {
		element: '#id_fechafinevento_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaInicioEntrenaOptions = {
		element: '#id_fechainicioentrena_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaFinEntrenaOptions = {
		element: '#id_fechafinentrena_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let eDisciplinas;
	let selectDisciplinas = [];
	let valueDisciplinas = [];
	let inputFechaInicioEvento = '';
	let inputFechaFinEvento = '';
	let inputFechaInicioEntrena = '';
	let inputFechaFinEntrena = '';
	let inputVigente = false;
	let inputVerificado = false;
	let inputEvento = '';
	let readSelectionPais;
	let inputEquipoRepresenta = '';
	let fileEvento;
	let fileEntrena;
	let download_archivoevento = '';
	let download_archivoentrena = '';
	let inputRepresentaPais = 0;
	const SI_NO = [
		{ id: 1, name: 'SI' },
		{ id: 2, name: 'NO' }
	];
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eDeportista = aData.eDeportista;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		eDisciplinas = await loadDataDisciplinas();
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eDeportista) {
			inputVigente = eDeportista.vigente ?? false;
			if (eDeportista.disciplina.length) {
				let ids = [];
				eDeportista.disciplina.forEach((dis) => {
					valueDisciplinas.push({
						id: dis['pk'],
						name: dis['descripcion']
					});
					ids.push(dis['pk']);
				});
				selectDisciplinas = ids;
			}
			if (eDeportista.paisevento) {
				readSelectionPais = {
					id: eDeportista.paisevento['pk'],
					name: eDeportista.paisevento['nombre']
				};
			}
			inputEquipoRepresenta = eDeportista.equiporepresenta ?? '';
			inputFechaInicioEvento = eDeportista.fechainicioevento ?? '';
			inputFechaFinEvento = eDeportista.fechafinevento ?? '';
			inputFechaInicioEntrena = eDeportista.fechainicioentrena ?? '';
			inputFechaFinEntrena = eDeportista.fechafinentrena ?? '';
			inputVerificado = eDeportista.verificado ?? false;
			inputRepresentaPais = eDeportista.representapais ?? 0;
			inputEvento = eDeportista.evento ?? '';
			if (eDeportista.download_archivoevento) {
				download_archivoevento = eDeportista.download_archivoevento;
			}
			if (eDeportista.download_archivoentrena) {
				download_archivoentrena = eDeportista.download_archivoentrena;
			}
		}

		await delay(2000);
		load = false;
	});

	const saveDeporteCulturaDeportista = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatoDeporte = document.getElementById('frmDatoDeporte');
		const formData = new FormData($frmDatoDeporte);
		formData.append('representapais', inputRepresentaPais.toString());
		if (selectDisciplinas != null) {
			let ids = [];
			selectDisciplinas.forEach((element) => {
				ids.push(element);
			});
			formData.append('disciplina', JSON.stringify(ids));
		}
		formData.append('evento', inputEvento);
		formData.append('equiporepresenta', inputEquipoRepresenta);
		if (readSelectionPais != null) {
			formData.append('paisevento', readSelectionPais.id);
		}
		const fechainicioevento = document.getElementById('id_fechainicioevento');
		const fechafinevento = document.getElementById('id_fechafinevento');
		if (fechainicioevento) {
			formData.append('fechainicioevento', fechainicioevento.value);
		}
		if (fechafinevento) {
			formData.append('fechafinevento', fechafinevento.value);
		}
		const fechainicioentrena = document.getElementById('id_fechainicioentrena');
		const fechafinentrena = document.getElementById('id_fechafinentrena');
		if (fechainicioentrena) {
			formData.append('fechainicioentrena', fechainicioentrena.value);
		}
		if (fechafinentrena) {
			formData.append('fechafinentrena', fechafinentrena.value);
		}
		if (fileEntrena) {
			formData.append('archivoentrena', fileEntrena.file);
		}
		if (fileEvento) {
			formData.append('archivoevento', fileEntrena.file);
		}
		if (eDeportista != undefined) {
			formData.append('id', eDeportista.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('action', 'saveDeporteCulturaDeportista');
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
				dispatch('actionRun', { action: 'saveDeporteCulturaDeportista' });
			}
		}
	};

	const handleFileSelectedArchivoEvento = (event) => {
		fileEvento = event.detail;
	};

	const handleFileRemovedArchivoEvento = () => {
		fileEvento = null;
	};

	const handleFileSelectedArchivoEntrena = (event) => {
		fileEntrena = event.detail;
	};

	const handleFileRemovedArchivoEntrena = () => {
		fileEntrena = null;
	};

	const changePais = (event) => {};
</script>

<Modal
	isOpen={true}
	toggle={mToggle}
	size="lg"
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
	backdrop="static"
>
	<ModalHeader toggle={mToggle} class="bg-primary text-white">
		<span class="text-white">{mTitle}</span>
	</ModalHeader>
	<ModalBody>
		{#if !load}
			<form action="javascript:;" id="frmDatoDeporte">
				<div class="row g-3">
					<div class="col-lg-4 col-md-4 col-12 ">
						<label for="id_representapais" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Representa al Ecuador:</label
						>
						<select
							class="form-select form-select-sm"
							aria-label=""
							id="id_representapais"
							bind:value={inputRepresentaPais}
						>
							<option value={0} selected> ----------- </option>
							{#each SI_NO as r}
								{#if inputRepresentaPais === r.id}
									<option value={r.id} selected>
										{r.name}
									</option>
								{:else}
									<option value={r.id}>
										{r.name}
									</option>
								{/if}
							{/each}
						</select>

						<div class="valid-feedback" id="id_representapais_validate">¡Se ve bien!</div>
					</div>
					<div class="col-lg-8 col-md-8 col-12 ">
						<label for="id_campoartistico" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Disciplinas deportivas:</label
						>
						{#if eDisciplinas}
							<FormMultiselect
								id="id_campoartistico"
								name="campoartistico"
								clases="form-select form-select-sm"
								itemId="id"
								label="name"
								items={eDisciplinas}
								value={valueDisciplinas}
								bind:justValue={selectDisciplinas}
							/>
						{/if}
						<div class="valid-feedback" id="id_campoartistico_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<label for="id_evento" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Evento participación:</label
						>
						<input
							type="text"
							class="form-control form-control-sm"
							id="id_evento"
							bind:value={inputEvento}
						/>
						<div class="valid-feedback" id="id_evento_validate">¡Se ve bien!</div>
					</div>
					<div class="col-lg-6 col-md-6 col-12 ">
						<label for="id_equiporepresenta" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Equipo representa:</label
						>
						<input
							type="text"
							class="form-control form-control-sm"
							id="id_equiporepresenta"
							bind:value={inputEquipoRepresenta}
						/>
						<div class="valid-feedback" id="id_equiporepresenta_validate">¡Se ve bien!</div>
					</div>
					<div class="col-lg-6 col-md-6 col-12 ">
						<label for="id_paisevento" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> País evento:</label
						>
						<FormSelectSearch
							inputId="id_paisevento"
							name="paisevento"
							bind:value={readSelectionPais}
							on:actionChangeSelectSearch={changePais}
							fetch={(query) => loadDataPaises(query)}
						/>
						<div class="valid-feedback" id="id_paisevento_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_fechainicioevento" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha inicio evento:</label
						>
						<Flatpickr
							options={flatpickrFechaInicioEventoOptions}
							bind:value={inputFechaInicioEvento}
							element="#id_fechainicioevento_element"
						>
							<div class="flatpickr input-group" id="id_fechainicioevento_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechainicioevento"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechainicioevento_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_fechafinevento" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha fin evento:</label
						>
						<Flatpickr
							options={flatpickrFechaFinEventoOptions}
							bind:value={inputFechaFinEvento}
							element="#id_fechafinevento_element"
						>
							<div class="flatpickr input-group" id="id_fechafinevento_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechafinevento"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechafinevento_validate">¡Se ve bien!</div>
					</div>

					<div class="col-md-6 col-12">
						<label for="id_fechainicioentrena" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha inicio entrena:</label
						>
						<Flatpickr
							options={flatpickrFechaInicioEntrenaOptions}
							bind:value={inputFechaInicioEntrena}
							element="#id_fechainicioentrena_element"
						>
							<div class="flatpickr input-group" id="id_fechainicioentrena_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechainicioentrena"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechainicioentrena_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_fechafinentrena" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha fin entrena:</label
						>
						<Flatpickr
							options={flatpickrFechaFinEntrenaOptions}
							bind:value={inputFechaFinEntrena}
							element="#id_fechafinentrena_element"
						>
							<div class="flatpickr input-group" id="id_fechafinentrena_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechafinentrena"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechafinentrena_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_archivoevento" class="form-label fw-bold">Archivo evento:</label>
						<FileUploader
							inputID="id_archivoevento"
							inputName="archivoevento"
							acceptedFileTypes={['application/pdf']}
							labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
							on:fileSelected={handleFileSelectedArchivoEvento}
							on:fileRemoved={handleFileRemovedArchivoEvento}
						/>
						<div class="text-center fs-6">
							<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
						{#if download_archivoevento != ''}
							<div class="fs-6">
								Tienes un archivo subido:
								<a
									title="Ver archivo"
									href={download_archivoevento}
									target="_blank"
									class="text-primary text-center">Ver archivo</a
								>
							</div>
						{/if}

						<div class="valid-feedback" id="id_archivoevento_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_archivoentrena" class="form-label fw-bold">Archivo entrena:</label>
						<FileUploader
							inputID="id_archivoentrena"
							inputName="archivoentrena"
							acceptedFileTypes={['application/pdf']}
							labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
							on:fileSelected={handleFileSelectedArchivoEntrena}
							on:fileRemoved={handleFileRemovedArchivoEntrena}
						/>
						<div class="text-center fs-6">
							<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
						</div>
						{#if download_archivoentrena != ''}
							<div class="fs-6">
								Tienes un archivo subido:
								<a
									title="Ver archivo"
									href={download_archivoentrena}
									target="_blank"
									class="text-primary text-center">Ver archivo</a
								>
							</div>
						{/if}

						<div class="valid-feedback" id="id_archivoentrena_validate">¡Se ve bien!</div>
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
			<Button color="warning" class="rounded-5 btn-sm" on:click={saveDeporteCulturaDeportista}
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
