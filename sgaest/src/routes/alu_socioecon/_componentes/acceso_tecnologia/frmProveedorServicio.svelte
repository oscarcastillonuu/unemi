<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { getProveedoresInternet as loadDataProveedores } from '$lib/utils/loadDataApi';
	import { customFormErrors, resetForms } from '$lib/utils/forms';
	export let aData;
	export let mToggle;
	export let mTitle;
	let eFichaSocioeconomica;
	let eProveedores;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let selectProveedorInternet = 0;
	let readProveedorInternet;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		await resetForms('none');
		mensaje_load = 'Consultado la información, espere por favor...';
		eProveedores = await loadDataProveedores();
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (aData.eFichaSocioeconomica) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica;
			if (eFichaSocioeconomica.proveedorinternet) {
				selectProveedorInternet = eFichaSocioeconomica.proveedorinternet['pk'] ?? 0;
				readProveedorInternet = {
					id: eFichaSocioeconomica.proveedorinternet['pk'],
					name: eFichaSocioeconomica.proveedorinternet['nombre']
				};
			}
		}
		await delay(2000);
		load = false;
	});

	const saveDatosAccesoTecnologia = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		await resetForms('none');
		const $frmProveedor = document.getElementById('frmProveedor');
		const formData = new FormData($frmProveedor);
		if (readProveedorInternet != null) {
			formData.append('proveedorinternet', readProveedorInternet.id);
		}
		else{
			formData.append('proveedorinternet', '0');
		}
		formData.append('field', 'proveedorinternet');
		formData.append('action', 'saveDatosAccesoTecnologia');
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
				dispatch('actionRun', { action: 'saveDatosAccesoTecnologia' });
			}
		}
	};

	const changeProveedor = (event) => {
		//console.log("change pais: ", event);
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
			<form action="javascript:;" id="frmProveedor">
				<div class="row g-3">
					<div class="col-12">
						<label for="id_proveedorinternet" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> ¿Cuál es su proveedor de servicio
							de internet?
						</label>
						<FormSelectSearch
							minQuery={1}
							inputId="id_proveedorinternet"
							name="proveedorinternet"
							bind:value={readProveedorInternet}
							on:actionChangeSelectSearch={changeProveedor}
							fetch={(query) => loadDataProveedores(query)}
						/>
						<!--<select
							class="form-select form-select-sm"
							aria-label=""
							id="id_proveedorinternet"
							bind:value={selectProveedorInternet}
						>
							<option value={0} selected> ----------- </option>
							{#each eProveedores as eProveedor}
								{#if selectProveedorInternet === eProveedor.id}
									<option value={eProveedor.id} selected>
										{eProveedor.name}
									</option>
								{:else}
									<option value={eProveedor.id}>
										{eProveedor.name}
									</option>
								{/if}
							{/each}
						</select>-->
						<div class="valid-feedback" id="id_proveedorinternet_validate">¡Se ve bien!</div>
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
			<Button color="primary" class="rounded-3 btn-sm" on:click={saveDatosAccesoTecnologia}
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