<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { getParentescos as loadParentescos } from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { numeric } from '$lib/formats/formatDecimal';

	export let aData;
	export let mToggle;
	export let mTitle;
	let ePersonaExtension;
	let eParentescos;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputContactoEmergencia = '';
	let inputTelefonoEmergencia = '';
	let selectParentescoPersona = 0;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePersonaExtension = aData.ePersonaExtension;
		mensaje_load = 'Consultado la información, espere por favor...';
		eParentescos = await loadParentescos();
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		inputContactoEmergencia = ePersonaExtension.contactoemergencia ?? '';
		inputTelefonoEmergencia = ePersonaExtension.telefonoemergencia ?? '';

		const parentesto = ePersonaExtension.parentescoemergencia;
		if (parentesto) {
			selectParentescoPersona = parentesto['pk'] ?? 0;
		}
		await delay(2000);
		load = false;
	});

	const saveDatosMedicoContactoEmergencia = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosMedicoContactoEmergencia = document.getElementById(
			'frmDatosMedicoContactoEmergencia'
		);
		const formData = new FormData($frmDatosMedicoContactoEmergencia);
		//const numeros = /^([0-9])*$/;
		const fecha = document.getElementById('id_nacimiento');

		formData.append('contactoemergencia', inputContactoEmergencia);
		formData.append('telefonoemergencia', inputTelefonoEmergencia);
		formData.append('parentescoemergencia', selectParentescoPersona.toString());

		formData.append('action', 'saveDatosMedicoContactoEmergencia');
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
				<form action="javascript:;" id="frmDatosMedicoContactoEmergencia">
					<div class="row g-3">
						<div class="col-12">
							<label for="id_contactoemergencia" class="form-label fw-bold"
								>Contacto de emergencia:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_contactoemergencia"
								bind:value={inputContactoEmergencia}
							/>
							<div class="valid-feedback" id="id_contactoemergencia_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6">
							<label for="id_telefonoemergencia" class="form-label fw-bold"
								>Teléfono de emergencia:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_telefonoemergencia"
								bind:value={inputTelefonoEmergencia}
							/>
							<div class="valid-feedback" id="id_telefonoemergencia_validate">¡Se ve bien!</div>
						</div>
						<div class="col-md-6">
							<label for="id_parentescoemergencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Parentesco:</label
							>
							{#if eParentescos}
								<select
									class="form-select form-select-sm"
									aria-label=""
									required
									id="id_parentescoemergencia"
									bind:value={selectParentescoPersona}
								>
									{#each eParentescos as eParentesco}
										{#if selectParentescoPersona === eParentesco.id}
											<option value={eParentesco.id} selected>
												{eParentesco.name}
											</option>
										{:else}
											<option value={eParentesco.id}>
												{eParentesco.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_parentescoemergencia_validate">¡Se ve bien!</div>
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
				<Button
					color="warning"
					class="rounded-5 btn-sm"
					on:click={saveDatosMedicoContactoEmergencia}><i class="fe fe-check" /> Guardar</Button
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
