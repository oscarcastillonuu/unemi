<script lang="ts">
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { addNotification } from '$lib/store/notificationStore';
	import Swal from 'sweetalert2';

	export let aData;
	export let mToggle;
	export let mOpenModal;
	export let mTitle;
	let eMatriculaSedeExamen = undefined;
	let terminos_examenes = undefined;
	let load = true;
	let acept_t_ex = false;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eMatriculaSedeExamen = aData ?? undefined;
		console.log('eMatriculaSedeExamen: ', eMatriculaSedeExamen);
		if (eMatriculaSedeExamen) {
			terminos_examenes = eMatriculaSedeExamen.terminos_examenes ?? {};
		}
		await delay(2000);
		load = false;
	});

	const actionCreateAcceptTerminosCondicionesExamen = async (isDemo) => {
		loading.setLoading(true, 'Consultando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual/examenes', {
			action: 'createAcceptTerminosCondicionesExamen',
			isDemo: isDemo
		});
		loading.setLoading(false, 'Consultando la información, espere por favor...');
		if (errors.length > 0) {
			addToast({ type: 'error', header: '¡ERROR!', body: errors[0].error });
			return false;
		} else {
			if (!res.isSuccess) {
				loading.setLoading(false, 'Consultando la información, espere por favor...');
				addToast({ type: 'error', header: '¡ERROR!', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				return false;
			} else {
				var a = document.createElement('a');
				a.target = '_blank';
				a.href = res.data.url_pdf;
				a.click();
				return true;

				//goto('/');
			}
		}
		return false;
	};

	const aceptarTerminoCondicionExamen = () => {
		const acepto_terminos = acept_t_ex;
		if (!acepto_terminos) {
			addNotification({
				msg: `Para continuar, favor acepte los términos y condiciones`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			return false;
		}
		const _acept_t = acepto_terminos ? 1 : 0;
		let texto = `Está a punto de confirmar lo términos y condiciones.\n¿Desea continuar?`;
		const mensaje = {
			html: `<b>${texto}</b>`,
			customClass: {
				cancelButton: 'btn-mini',
				confirmButton: 'btn-confirm'
			},
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#FE9900',
			//cancelButtonColor: '#d33',
			confirmButtonText: `Si, deseo hacerlo!`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje).then(async (result) => {
			if (result.value) {
				const result = await actionCreateAcceptTerminosCondicionesExamen(false);
				loading.setLoading(true, 'Cargando, espere por favor...');
				if (result === true) {
					mOpenModal = !mOpenModal;
					//goto('/alu_documentos/examenes');
					window.location.reload();
				}
				else{
					loading.setLoading(false, 'Consultando la información, espere por favor...');
				}
			}
		});
	};
</script>

{#if terminos_examenes}
	<Modal
		isOpen={mOpenModal}
		toggle={mToggle}
		size="lg"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		{#if mTitle}
			<ModalHeader toggle={mToggle} class="bg-primary text-white">
				<span class="text-white">{mTitle}</span>
			</ModalHeader>
		{/if}
		<ModalBody>
			{#if !load}
				{#if terminos_examenes}
					<div class="row g-3">
						<div class="col-12 ">
							<div>{@html terminos_examenes.text ?? ''}</div>
						</div>
						<div class="col-12 ">
							<div class="d-grid gap-2 d-md-flex justify-content-md-end">
								<a
									class="text-primary"
									href="javascript:;"
									on:click={() => actionCreateAcceptTerminosCondicionesExamen(true)}
									>Ver borrador de términos y condiciones para rendir los exámenes
								</a>
							</div>
						</div>
					</div>
				{/if}
			{:else}
				<div class="row justify-content-center align-items-center p-5 m-0">
					<div class="col-auto text-center">
						<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
						<h3>Verificando la información, espere por favor...</h3>
					</div>
				</div>
			{/if}
		</ModalBody>

		<ModalFooter class="pb-3 mb-3 d-lg-flex justify-content-between align-items-center">
			<div class="mb-3 mb-lg-0">
				{#if !load}
					<div class="form-check">
						<input
							class="form-check-input"
							type="checkbox"
							value=""
							id="invalidCheck"
							required
							bind:checked={acept_t_ex}
						/>
						<label class="form-check-label fw-bold" for="invalidCheck">
							Acepto los términos y condiciones
						</label>
						<!--<div class="invalid-feedback">You must agree before submitting.</div>-->
					</div>
				{/if}
			</div>
			<div class="d-flex">
				<Button color="warning" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
				{#if !load}
					<Button
						color="primary"
						class="rounded-3 btn-sm mx-1"
						on:click={() => aceptarTerminoCondicionExamen()}>Guardar</Button
					>
				{/if}
			</div>
		</ModalFooter>
	</Modal>
{/if}
