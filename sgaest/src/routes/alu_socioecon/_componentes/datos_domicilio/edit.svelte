<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import {
		getPaises as loadDataPaises,
		getProvinicias as loadDataProvincias,
		getCantones as loadDataCantones,
		getParroquias as loadDataParroquias
	} from '$lib/utils/loadDataApi';
	import { customFormErrors, resetForms } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	export let aData;
	export let mToggle;
	let ePersona;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let readSelectionPais;
	let readSelectionProvincia;
	let readSelectionCanton;
	let readSelectionParroquia;
	let inputDireccion = '';
	let inputDireccion2 = '';
	let inputNumDireccion = '';
	let inputSector = '';
	let inputReferencia = '';
	let inputTelefono = '';
	let inputTelefonoConv = '';
	let inputOperadora = 0;
	let inputSectorLugar = 0;
	let fileCroquis;
	let filePlanillaLuz;
	let download_croquis = '';
	let download_planilla_luz = '';
	const eOperadoras = [
		{ id: 1, name: 'Claro' },
		{ id: 2, name: 'Movistar' },
		{ id: 3, name: 'CNT' },
		{ id: 4, name: 'Otra' },
		{ id: 5, name: 'Tuenti' }
	];

	const eSectores = [
		{ id: 1, name: 'Urbana' },
		{ id: 2, name: 'Rural' }
	];

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		await resetForms('none');
		ePersona = aData.ePersona;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';

		if (ePersona.pais) {
			readSelectionPais = {
				id: ePersona.pais['pk'],
				name: ePersona.pais['nombre']
			};
		}
		if (ePersona.provincia) {
			readSelectionProvincia = {
				id: ePersona.provincia['pk'],
				name: ePersona.provincia['nombre']
			};
		}
		if (ePersona.canton) {
			readSelectionCanton = {
				id: ePersona.canton['pk'],
				name: ePersona.canton['nombre']
			};
		}
		if (ePersona.parroquia) {
			readSelectionParroquia = {
				id: ePersona.parroquia['pk'],
				name: ePersona.parroquia['nombre']
			};
		}

		inputDireccion = ePersona.direccion ?? '';
		inputDireccion2 = ePersona.direccion2 ?? '';
		inputNumDireccion = ePersona.num_direccion ?? '';
		inputSector = ePersona.sector ?? '';
		inputReferencia = ePersona.referencia ?? '';
		inputOperadora = ePersona.tipocelular ?? 0;
		inputTelefono = ePersona.telefono ?? '';
		inputTelefonoConv = ePersona.telefono_conv ?? '';
		inputSectorLugar = ePersona.sectorlugar ?? 0;
		download_croquis = ePersona.download_croquis ?? '';
		download_planilla_luz = ePersona.download_planilla_luz ?? '';
		await delay(2000);
		load = false;
	});

	const saveDatosDomicilio = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		await resetForms('none');
		const $frmDatosDomicilio = document.getElementById('frmDatosDomicilio');
		const formData = new FormData($frmDatosDomicilio);
		if (readSelectionPais != null) {
			formData.append('pais', readSelectionPais.id);
		}
		if (readSelectionProvincia != null) {
			formData.append('provincia', readSelectionProvincia.id);
		}
		if (readSelectionCanton != null) {
			formData.append('canton', readSelectionCanton.id);
		}
		if (readSelectionParroquia != null) {
			formData.append('parroquia', readSelectionParroquia.id);
		}
		formData.append('direccion', inputDireccion);
		formData.append('direccion2', inputDireccion2);
		formData.append('num_direccion', inputNumDireccion);
		formData.append('sector', inputSector);
		formData.append('referencia', inputReferencia);
		formData.append('tipocelular', inputOperadora.toString());
		formData.append('telefono', inputTelefono);
		formData.append('telefono_conv', inputTelefonoConv);
		formData.append('sectorlugar', inputSectorLugar.toString());
		if (fileCroquis) {
			formData.append('archivocroquis', fileCroquis.file);
		}
		if (filePlanillaLuz) {
			formData.append('archivoplanillaluz', filePlanillaLuz.file);
		}
		formData.append('action', 'saveDatosDomicilio');
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
					await resetForms('block');
				}

				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'saveDatosDomicilio' });
			}
		}
	};
	const changePais = (event) => {
		//console.log("change pais: ", event);
		readSelectionProvincia = null;
		readSelectionCanton = null;
		readSelectionParroquia = null;
	};
	const changeProvincia = (event) => {
		//console.log("change provincia: ", event);
		readSelectionCanton = null;
		readSelectionParroquia = null;
	};
	const changeCanton = (event) => {
		//console.log("change canton: ", event);
		readSelectionParroquia = null;
	};

	const handleFileSelectedCroquis = (event) => {
		fileCroquis = event.detail;
	};

	const handleFileRemovedCroquis = () => {
		fileCroquis = null;
	};

	const handleFileSelectedPlanillaLuz = (event) => {
		filePlanillaLuz = event.detail;
	};

	const handleFileRemovedPlanillaLuz = () => {
		filePlanillaLuz = null;
	};
</script>

{#if ePersona}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size="lg"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">Actualizar datos de domicilio o residencia actual</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmDatosDomicilio">
					<div class="row g-3">
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_pais" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> País:</label
							>
							<FormSelectSearch
								inputId="id_pais"
								name="pais"
								bind:value={readSelectionPais}
								on:actionChangeSelectSearch={changePais}
								fetch={(query) => loadDataPaises(query)}
							/>
							<div class="valid-feedback" id="id_pais_validate">¡Se ve bien!</div>
						</div>
						{#if readSelectionPais != null && readSelectionPais.id === 1}
							<div class="col-lg-6 col-md-6 col-12 mb-1">
								<label for="id_provincia" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Provincia:</label
								>
								<FormSelectSearch
									inputId="id_provincia"
									name="provincia"
									parent="id_pais"
									bind:value={readSelectionProvincia}
									on:actionChangeSelectSearch={changeProvincia}
									fetch={(query) => loadDataProvincias(readSelectionPais.id, query)}
								/>
								<div class="valid-feedback" id="id_provincia_validate">¡Se ve bien!</div>
							</div>
							{#if readSelectionProvincia != null}
								<div class="col-lg-6 col-md-6 col-12 mb-1">
									<label for="id_canton" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Cantón:</label
									>
									<FormSelectSearch
										inputId="id_canton"
										name="canton"
										parent="id_provincia"
										bind:value={readSelectionCanton}
										on:actionChangeSelectSearch={changeCanton}
										fetch={(query) => loadDataCantones(readSelectionProvincia.id, query)}
									/>
									<div class="valid-feedback" id="id_canton_validate">¡Se ve bien!</div>
								</div>
							{/if}
							{#if readSelectionCanton != null}
								<div class="col-lg-6 col-md-6 col-12 mb-1">
									<label for="id_parroquia" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Parroquia:</label
									>
									<FormSelectSearch
										inputId="id_parroquia"
										name="parroquia"
										parent="id_canton"
										bind:value={readSelectionParroquia}
										fetch={(query) => loadDataParroquias(readSelectionCanton.id, query)}
									/>
									<div class="valid-feedback" id="id_parroquia_validate">¡Se ve bien!</div>
								</div>
							{/if}
						{/if}
					</div>
					<div class="row g-3 mt-1">
						<div class="col-lg-6 col-md-12 col-12 mb-1">
							<label for="id_direccion" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Calle principal:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_direccion"
								bind:value={inputDireccion}
							/>
							<div class="valid-feedback" id="id_direccion_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-12 col-12 mb-1">
							<label for="id_direccion2" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Calle secundaria:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_direccion2"
								bind:value={inputDireccion2}
							/>
							<div class="valid-feedback" id="id_direccion2_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-3 col-md-6 col-12 mb-1">
							<label for="id_num_direccion" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Número de casa:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_num_direccion"
								bind:value={inputNumDireccion}
							/>
							<div class="valid-feedback" id="id_num_direccion_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-3 col-md-6 col-12 mb-1">
							<label for="id_sector" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Sector:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_sector"
								bind:value={inputSector}
							/>
							<div class="valid-feedback" id="id_sector_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-12 col-12 mb-1">
							<label for="id_referencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Referencia:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_referencia"
								bind:value={inputReferencia}
							/>
							<div class="valid-feedback" id="id_referencia_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-3 col-md-6 col-12 mb-1">
							<label for="id_tipocelular" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Operadora celular:</label
							>
							<select
								class="form-select form-select-sm"
								aria-label=""
								id="id_tipocelular"
								bind:value={inputOperadora}
							>
								<option value={0} selected> ----------- </option>
								{#each eOperadoras as Operadora}
									{#if inputOperadora === Operadora.id}
										<option value={Operadora.id} selected>
											{Operadora.name}
										</option>
									{:else}
										<option value={Operadora.id}>
											{Operadora.name}
										</option>
									{/if}
								{/each}
							</select>

							<div class="valid-feedback" id="id_tipocelular_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-3 col-md-6 col-12 mb-1">
							<label for="id_telefono" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Teléfono celular:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_telefono"
								bind:value={inputTelefono}
							/>
							<div class="valid-feedback" id="id_telefono_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-3 col-md-6 col-12 mb-1">
							<label for="id_telefono_conv" class="form-label fw-bold"
								>Teléfono domicilio (fijo):</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_telefono_conv"
								bind:value={inputTelefonoConv}
							/>
							<div class="valid-feedback" id="id_telefono_conv_validate">¡Se ve bien!</div>
						</div>

						<div class="col-lg-3 col-md-6 col-12 mb-1">
							<label for="id_sectorlugar" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Zona residencia:</label
							>
							<select
								class="form-select form-select-sm"
								aria-label=""
								id="id_sectorlugar"
								bind:value={inputSectorLugar}
							>
								<option value={0} selected> ----------- </option>
								{#each eSectores as sector}
									{#if inputSectorLugar === sector.id}
										<option value={sector.id} selected>
											{sector.name}
										</option>
									{:else}
										<option value={sector.id}>
											{sector.name}
										</option>
									{/if}
								{/each}
							</select>

							<div class="valid-feedback" id="id_sectorlugar_validate">¡Se ve bien!</div>
						</div>
					</div>
					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-md-12 col-lg-12 col-12 mb-1">
							<label for="id_archivocroquis" class="form-label fw-bold">Croquis:</label>
							<FileUploader
								inputID="id_archivocroquis"
								inputName="archivocroquis"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedCroquis}
								on:fileRemoved={handleFileRemovedCroquis}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
							{#if download_croquis != ''}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={download_croquis}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivocroquis_validate">¡Se ve bien!</div>
						</div>

						<div class="col-md-12 col-lg-12 col-12 mb-1">
							<label for="id_archivoplanillaluz" class="form-label fw-bold"
								>Planilla de energia eléctrica:</label
							>
							<FileUploader
								inputID="id_archivoplanillaluz"
								inputName="archivoplanillaluz"
								acceptedFileTypes={['application/pdf']}
								labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
								on:fileSelected={handleFileSelectedPlanillaLuz}
								on:fileRemoved={handleFileRemovedPlanillaLuz}
							/>
							<div class="text-center fs-6">
								<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
							</div>
							{#if download_planilla_luz != ''}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={download_planilla_luz}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivoplanillaluz_validate">¡Se ve bien!</div>
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
			<Button color="secondary" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
			{#if !load}
				<Button color="primary" class="rounded-3 btn-sm" on:click={saveDatosDomicilio}
					>Guardar</Button
				>
			{/if}
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