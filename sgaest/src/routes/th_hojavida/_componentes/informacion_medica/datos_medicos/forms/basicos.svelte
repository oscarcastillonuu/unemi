<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { getTiposSangres as loadTipos } from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { numeric } from '$lib/formats/formatDecimal';

	export let aData;
	export let mToggle;
	export let mTitle;
	let ePersonaExtension;
	let eTipos;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputCarneIESS = '';
	let inputPeso = '';
	let inputTalla = '';
	let selectTipoSangre = 0;
	let fileSangre;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePersonaExtension = aData.ePersonaExtension;
		mensaje_load = 'Consultado la información, espere por favor...';
		eTipos = await loadTipos();
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		inputCarneIESS = ePersonaExtension.carnetiess ?? '';
		inputPeso = ePersonaExtension.peso ?? '';
		inputTalla = ePersonaExtension.talla ?? '';

		const tipo = ePersonaExtension.tipo_sangre;
		if (tipo) {
			selectTipoSangre = tipo['pk'] ?? 0;
		}
		await delay(2000);
		load = false;
	});

	const saveDatosMedicoBasico = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosBasicoMedico = document.getElementById('frmDatosBasicoMedico');
		const formData = new FormData($frmDatosBasicoMedico);
		//const numeros = /^([0-9])*$/;
		const fecha = document.getElementById('id_nacimiento');

		formData.append('carnetiess', inputCarneIESS);
		formData.append('peso', inputPeso);
		formData.append('talla', inputTalla);
		formData.append('sangre', selectTipoSangre.toString());
		if (fileSangre) {
			formData.append('archivo', fileSangre.file);
		}

		formData.append('action', 'saveDatosMedicoBasico');
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

	const handleFileSelectedSangre = (event) => {
		fileSangre = event.detail;
	};

	const handleFileRemovedSangre = () => {
		fileSangre = null;
	};
</script>

{#if ePersonaExtension}
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
				<form action="javascript:;" id="frmDatosBasicoMedico">
					<div class="row g-3">
						<div class="col-md-6">
							<label for="id_carnetiess" class="form-label fw-bold">Carnet IESS:</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_carnetiess"
								bind:value={inputCarneIESS}
							/>
							<div class="valid-feedback" id="id_carnetiess_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6">
							<label for="id_sangre" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Tipo de sangre:</label
							>
							{#if eTipos}
								<select
									class="form-select form-select-sm"
									aria-label=""
									required
									id="id_sangre"
									bind:value={selectTipoSangre}
								>
									{#each eTipos as eTipo}
										{#if selectTipoSangre === eTipo.id}
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
							{/if}
							<div class="valid-feedback" id="id_sangre_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6">
							<label for="id_peso" class="form-label fw-bold">Peso (kg):</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_peso"
								on:keyup={() => numeric('id_peso', 0, 1000, 2)}
								bind:value={inputPeso}
							/>
							<div class="valid-feedback" id="id_peso_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6">
							<label for="id_talla" class="form-label fw-bold">Talla (mts):</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_talla"
								on:keyup={() => numeric('id_talla', 0, 10, 2)}
								bind:value={inputTalla}
							/>
							<div class="valid-feedback" id="id_talla_validate">¡Se ve bien!</div>
						</div>
					</div>
					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-12">
							<label for="id_documento_archivo" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Certificado Tipo Sangre:</label
							>
							{#if ePersonaExtension.estadotiposangre != 2}
								<FileUploader
									inputID="id_sangre_archivo"
									inputName="sangre_archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedSangre}
									on:fileRemoved={handleFileRemovedSangre}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if ePersonaExtension.download_archivosangre}
								<div class="fs-6">
									Tienes un certificado subido:
									<a
										title="Ver archivo"
										href={ePersonaExtension.download_archivosangre}
										target="_blank"
										class="text-primary text-center">Ver certificado</a
									>
								</div>
							{/if}

							<div class="valid-feedback" id="id_sangre_archivo_validate">¡Se ve bien!</div>
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
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosMedicoBasico}
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
