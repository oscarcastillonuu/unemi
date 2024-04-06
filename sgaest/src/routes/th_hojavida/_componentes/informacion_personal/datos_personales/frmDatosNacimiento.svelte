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
	export let aData;
	export let mTitle;
	export let mToggle;
	let ePersona;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let readSelectionPais;
	let readSelectionProvincia;
	let readSelectionCanton;
	let readSelectionParroquia;
	let selectionPais;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		await resetForms('none');
		ePersona = aData.ePersona;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';

		if (ePersona.paisnacimiento) {
			selectionPais = ePersona.paisnacimiento['pk'] ?? null;
			readSelectionPais = {
				id: ePersona.paisnacimiento['pk'],
				name: ePersona.paisnacimiento['nombre']
			};
		}
		if (ePersona.provincianacimiento) {
			readSelectionProvincia = {
				id: ePersona.provincianacimiento['pk'],
				name: ePersona.provincianacimiento['nombre']
			};
		}
		if (ePersona.cantonnacimiento) {
			readSelectionCanton = {
				id: ePersona.cantonnacimiento['pk'],
				name: ePersona.cantonnacimiento['nombre']
			};
		}
		if (ePersona.parroquianacimiento) {
			readSelectionParroquia = {
				id: ePersona.parroquianacimiento['pk'],
				name: ePersona.parroquianacimiento['nombre']
			};
		}

		await delay(2000);
		load = false;
	});

	const saveDatosPersonalesNacimiento = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		await resetForms('none');
		const $frmDatosNacimiento = document.getElementById('frmDatosNacimiento');
		const formData = new FormData($frmDatosNacimiento);
		if (readSelectionPais != null) {
			formData.append('paisnacimiento', readSelectionPais.id);
		}
		if (readSelectionProvincia != null) {
			formData.append('provincianacimiento', readSelectionProvincia.id);
		}
		if (readSelectionCanton != null) {
			formData.append('cantonnacimiento', readSelectionCanton.id);
		}
		if (readSelectionParroquia != null) {
			formData.append('parroquianacimiento', readSelectionParroquia.id);
		}

		formData.append('action', 'saveDatosPersonalesNacimiento');
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
					await resetForms('block');
				}

				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'saveDatosPersonalesNacimiento' });
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
</script>

{#if ePersona}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size="md"
		class="modal-dialog modal-dialog-centered modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmDatosNacimiento">
					<div class="row g-3">
						<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
							<label for="id_paisnacimiento" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> País:</label
							>
							<FormSelectSearch
								inputId="id_paisnacimiento"
								name="paisnacimiento"
								bind:value={readSelectionPais}
								on:actionChangeSelectSearch={changePais}
								fetch={(query) => loadDataPaises(query)}
							/>
							<div class="valid-feedback" id="id_paisnacimiento_validate">¡Se ve bien!</div>
						</div>
						{#if readSelectionPais != null && readSelectionPais.id === 1}
							<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
								<label for="id_provincianacimiento" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Provincia:</label
								>
								<FormSelectSearch
									inputId="id_provincianacimiento"
									name="provincianacimiento"
									parent="id_paisnacimiento"
									bind:value={readSelectionProvincia}
									on:actionChangeSelectSearch={changeProvincia}
									fetch={(query) => loadDataProvincias(readSelectionPais.id, query)}
								/>
								<div class="valid-feedback" id="id_provincianacimiento_validate">¡Se ve bien!</div>
							</div>
							{#if readSelectionProvincia != null}
								<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
									<label for="id_cantonnacimiento" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Cantón:</label
									>
									<FormSelectSearch
										inputId="id_cantonnacimiento"
										name="cantonnacimiento"
										parent="id_provincianacimiento"
										bind:value={readSelectionCanton}
										on:actionChangeSelectSearch={changeCanton}
										fetch={(query) => loadDataCantones(readSelectionProvincia.id, query)}
									/>
									<div class="valid-feedback" id="id_cantonnacimiento_validate">¡Se ve bien!</div>
								</div>
							{/if}
							{#if readSelectionCanton != null}
								<div class="col-lg-6 col-md-6 col-12 mb-1 mb-lg-2">
									<label for="id_parroquianacimiento" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Parroquia:</label
									>
									<FormSelectSearch
										inputId="id_parroquianacimiento"
										name="parroquianacimiento"
										parent="id_cantonnacimiento"
										bind:value={readSelectionParroquia}
										fetch={(query) => loadDataParroquias(readSelectionCanton.id, query)}
									/>
									<div class="valid-feedback" id="id_parroquianacimiento_validate">
										¡Se ve bien!
									</div>
								</div>
							{/if}
						{/if}
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
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosPersonalesNacimiento}
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
