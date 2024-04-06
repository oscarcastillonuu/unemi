<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors, resetForms } from '$lib/utils/forms';
	import { numeric } from '$lib/formats/formatDecimal';
	export let aData;
	export let mToggle;
	export let mTitle;
	let eFichaSocioeconomica;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputHorasTrabajoFueraHogar = 0;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		await resetForms('none');
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (aData.eFichaSocioeconomica) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica;
			if (eFichaSocioeconomica.horastrabajofuera) {
				inputHorasTrabajoFueraHogar = eFichaSocioeconomica.horastrabajofuera ?? 0;
			}
		}
		await delay(2000);
		load = false;
	});

	const saveDatosActividadExtracurricular = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		await resetForms('none');
		const $frmActividad = document.getElementById('frmActividad');
		const formData = new FormData($frmActividad);
		if (inputHorasTrabajoFueraHogar != null) {
			formData.append('horastrabajofuera', inputHorasTrabajoFueraHogar.toString());
		} else {
			formData.append('horastrabajofuera', '0');
		}
		formData.append('field', 'horastrabajofuera');
		formData.append('action', 'saveDatosActividadExtracurricular');
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
				dispatch('actionRun', { action: 'saveDatosActividadExtracurricular' });
			}
		}
	};
</script>

<Modal
	isOpen={true}
	toggle={mToggle}
	size="md"
	class="modal-dialog modal-dialog-centered modal-fullscreen-lg-down"
	backdrop="static"
>
	<ModalHeader toggle={mToggle} class="bg-primary text-white">
		<span class="text-white">{mTitle ?? 'Nivel de estudio'}</span>
	</ModalHeader>
	<ModalBody>
		{#if !load}
			<form action="javascript:;" id="frmActividad">
				<div class="row g-3">
					<div class="col-12">
						<label for="id_horastrabajofuera" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Horas de trabajo fuera de
							casa
						</label>
						<input
							type="number"
							class="form-control form-control-sm"
							aria-label=""
							id="id_horastrabajofuera"
							bind:value={inputHorasTrabajoFueraHogar}
							on:keyup={() => numeric('id_horastrabajofuera', 0, 1000, 0)}
						/>

						<div class="valid-feedback" id="id_horastrabajofuera_validate">¡Se ve bien!</div>
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
			<Button color="primary" class="rounded-3 btn-sm" on:click={saveDatosActividadExtracurricular}
				>Guardar</Button
			>
		{/if}
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