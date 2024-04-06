<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET, logOutUser } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Cambio de clave';
		let veryNeedChangePassword = false;
		let isError = false;
		let ePersona;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			//const dataSession = JSON.parse(ds);
			const [res, errors] = await apiPOST(fetch, 'changepassword', {
				action: 'veryNeedChangePassword'
			});
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				isError = true;
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					isError = true;
				} else {
					veryNeedChangePassword = res.data.veryNeedChangePassword;
					isError = false;
					ePersona = res.data.ePersona;
					if (!veryNeedChangePassword) {
						return {
							status: 302,
							redirect: '/'
						};
					}
				}
			}
		} else {
			isError = true;
		}

		return {
			props: {
				Title,
				veryNeedChangePassword,
				isError,
				ePersona
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponentChangePassword from '$components/ChangePassword/ChangePassword.svelte';
	import { Spinner } from 'sveltestrap';
	import Automatricula from '../alu_matricula/_Pregrado/_automatricula.svelte';
	export let Title;
	export let veryNeedChangePassword;
	export let isError;
	export let ePersona;
	let itemsBreadCrumb = [{ text: 'Cambio de clave', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let modalTitle = '';
	let modalDetalleContent;
	let aDataModal;
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (isError) {
			await logOutUser();
		}
		if (ePersona) {
			mOpenModalGenerico = true;
			modalDetalleContent = ComponentChangePassword;
			modalTitle = 'Cambiar contraseña';
			aDataModal = { ePersona: ePersona };
			load = false;
		}
	});
	const closeModal = async () => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `Se cambiado correctamente la contraseña`,
			type: 'success',
			icon: 'success',
			showCancelButton: false,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Aceptar',
			cancelButtonText: 'Cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					logOutUser();
				}
			})
			.catch((error) => {
				loading.setLoading(true, 'Cargando, espere por favor...');
				logOutUser();
			});
	};
	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModal') {
			closeModal();
		}
	};
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>
{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
	<section class="section">
		<div class="container">
			<div class="row">
				<div class="col-12 d-flex">
					<div class="card flex-fill w-100">
						<div class="card-header">
							<h5 class="card-title">Cambio de contraseña</h5>
						</div>
						<div class="card-body">
							<svelte:component
								this={ComponentChangePassword}
								aData={aDataModal}
								on:actionRun={actionRun}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>
{:else}
	<div
		class="m-0 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
