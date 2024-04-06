<script lang="ts">
	import { apiPOST, apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import StarRating from '$components/StarRating/StarRating.svelte';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	export let mClass;
	export let mSize;
	let eSolicitud;
	const dispatch = createEventDispatcher();

	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let rating = null;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eSolicitud = aData.eSolicitud;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);

		mensaje_load = 'Cargando la información, espere por favor...';
		rating = null;

		await delay(2000);
		load = false;
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'handleChangeRate') {
			rating = detail.rating ?? null;
		}
	};

	const saveEncuesta = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
			id: eSolicitud.pk,
			rating: rating,
			action: 'saveEncuesta'
		});
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

				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'saveEncuesta' });
			}
		}
	};
</script>

{#if mOpenModal}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size={mSize}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmSolicitud">
					<div class="">
						<h3 class="mb-4">¿Cómo calificaría la tutoría recibida por parte del profesor?</h3>
						<hr />
						<p class="text-center">
							<StarRating on:actionRun={actionRun} />
						</p>
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
				{#if rating != null}
					<Button color="warning" class="rounded-5 btn-sm" on:click={saveEncuesta}
						><i class="fe fe-check" /> Guardar</Button
					>
				{/if}
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
