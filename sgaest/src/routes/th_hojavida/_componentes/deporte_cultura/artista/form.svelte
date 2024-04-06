<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	import { getCamposArtisticos as loadCamposArtisticos } from '$lib/utils/loadDataApi';
	import FormMultiselect from '$components/Formulario/Multiselect.svelte';
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	let eArtista;
	const dispatch = createEventDispatcher();
	const flatpickrFechaInicioOptions = {
		element: '#id_fechainicioensayo_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaFinOptions = {
		element: '#id_fechafinensayo_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputFechaInicioEnsayo = '';
	let inputFechaFinEnsayo = '';
	let inputVigente = false;
	let inputVerificado = false;
	let selectCamposArtisticos = [];
	let valueCamposArtisticos = [];
	let inputObservacion = '';
	let inputGrupoPertenece = '';
	let eCampoArtisticos;
	let download_archivo = '';
	let fileArtista;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eArtista = aData.eArtista;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		eCampoArtisticos = await loadCamposArtisticos();
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eArtista) {
			inputVigente = eArtista.vigente ?? false;
			if (eArtista.campoartistico.length) {
				let ids = [];
				eArtista.campoartistico.forEach((eCampo) => {
					valueCamposArtisticos.push({
						id: eCampo['pk'],
						name: eCampo['descripcion']
					});
					ids.push(eCampo['pk']);
				});
				selectCamposArtisticos = ids;
			}
			inputGrupoPertenece = eArtista.grupopertenece ?? '';
			inputObservacion = eArtista.observacion ?? '';
			inputFechaInicioEnsayo = eArtista.fechainicioensayo ?? '';
			inputFechaFinEnsayo = eArtista.fechafinensayo ?? '';
			inputVerificado = eArtista.verificado ?? false;
			if (eArtista.download_archivo) {
				download_archivo = eArtista.download_archivo;
			}
		}

		await delay(2000);
		load = false;
	});

	const saveDeporteCulturaArtista = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatoArtista = document.getElementById('frmDatoArtista');
		const formData = new FormData($frmDatoArtista);

		if (selectCamposArtisticos != null) {
			let ids = [];
			selectCamposArtisticos.forEach((element) => {
				ids.push(element);
			});
			formData.append('campoartistico', JSON.stringify(ids));
		}
		const fechainicioensayo = document.getElementById('id_fechainicioensayo');
		const fechafinensayo = document.getElementById('id_fechafinensayo');
		formData.append('grupopertenece', inputGrupoPertenece);
		if (fechainicioensayo) {
			formData.append('fechainicioensayo', fechainicioensayo.value);
		}
		if (fechafinensayo) {
			formData.append('fechafinensayo', fechafinensayo.value);
		}
		if (fileArtista) {
			formData.append('archivo', fileArtista.file);
		}
		if (eArtista != undefined) {
			formData.append('id', eArtista.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('action', 'saveDeporteCulturaArtista');
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
				dispatch('actionRun', { action: 'saveDeporteCulturaArtista' });
			}
		}
	};

	const handleFileSelectedArchivo = (event) => {
		fileArtista = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileArtista = null;
	};
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
			<form action="javascript:;" id="frmDatoArtista">
				<div class="row g-3">
					<div class="col-12">
						<label for="id_campoartistico" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Campo artístico:</label
						>
						{#if eCampoArtisticos}
							<FormMultiselect
								id="id_campoartistico"
								name="campoartistico"
								clases="form-control form-control-sm"
								itemId="id"
								label="name"
								items={eCampoArtisticos}
								value={valueCamposArtisticos}
								bind:justValue={selectCamposArtisticos}
							/>
						{/if}
						<div class="valid-feedback" id="id_campoartistico_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<label for="id_grupopertenece" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Grupo pertenece:</label
						>
						<input
							type="text"
							class="form-control form-control-sm"
							id="id_grupopertenece"
							bind:value={inputGrupoPertenece}
						/>
						<div class="valid-feedback" id="id_grupopertenece_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_fechainicioembarazo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha inicio ensayos:</label
						>
						<Flatpickr
							options={flatpickrFechaInicioOptions}
							bind:value={inputFechaInicioEnsayo}
							element="#id_fechainicioensayo_element"
						>
							<div class="flatpickr input-group" id="id_fechainicioensayo_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechainicioensayo"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechainicioensayo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-6 col-12">
						<label for="id_fechafinensayo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha fin ensayos:</label
						>
						<Flatpickr
							options={flatpickrFechaFinOptions}
							bind:value={inputFechaFinEnsayo}
							element="#id_fechafinensayo_element"
						>
							<div class="flatpickr input-group" id="id_fechafinensayo_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechafinensayo"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechafinensayo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<label for="id_archivo" class="form-label fw-bold">Archivo del grupo:</label>
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
			<Button color="warning" class="rounded-5 btn-sm" on:click={saveDeporteCulturaArtista}
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
