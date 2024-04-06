<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';
	import PanelMatricula  from './panelMatricula.svelte'
	import ModuleError from './_Errors.svelte';
	import { Spinner, Tooltip } from 'sveltestrap';
	import {
		Button,
		Icon,
		Modal,
		ModalBody,
		ModalFooter,
		ModalHeader,
		Tooltip,
		Alert,
		Badge,
		ButtonDropdown,
		DropdownItem,
		DropdownMenu,
		DropdownToggle,
		Form,
		FormGroup,
		Input,
		Label,
		FormText,
		Offcanvas
	} from 'sveltestrap';
	export const load: ({fetch}: { fetch: any }) => Promise<string | { redirect: string; status: number } | { redirect: string; status: number } | { props: { data: ObjectConstructor; message_error: any; is_error: boolean } }> = async ({ fetch }) => {
		let data = Object;
		let is_error = false;
		let tiene_matricula = false;
		let message_error = undefined;
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/alu_automatriculamodulos', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {

			} else {
				if (!res.isSuccess) {
					message_error = res.message ;
					is_error = true;
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					}
					if (!res.isSuccess) {
						message_error = res.message;
						is_error = true;
					} else {
						message_error = '';
						is_error = false;
						data = res.data;
					}
				} else {
					data = res.data;
				}
			}
		}
		return {
			props: {
				data,
				message_error,
				is_error


			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import OffCanvasGenerico from '$components/Alumno/OffCanvasModal.svelte';

	let aDataModal = {};
	let aplacement = '';
	let modalDetalleOffCanvasContent;
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenOffCanvasGenerico = false;
	let modalTitle = '';
	let load = true;
	export let data;
	export let message_error;
	export let is_error;

	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	const mToggleOffCanvasGenerico = () => (mOpenOffCanvasGenerico = !mOpenOffCanvasGenerico);
	let itemsBreadCrumb = [
		{
			text: 'Matriculación módulos inglés',
			active: true,
			href: undefined
		}
	];
	let backBreadCrumb = {
		href: '/',
		text: 'Atrás'
	};
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (data !== undefined) {
			load = false;
		}
	});

	const loadAjax = async (data, url, method = undefined) =>
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
				const [res, errors] = await apiPOST(fetch, url, data);
				if (errors.length > 0) {
					reject({
						error: true,
						message: errors[0].error
					});
				} else {
					resolve({
						error: false,
						value: res
					});
				}
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
				if (errors.length > 0) {
					reject({
						error: true,
						message: errors[0].error
					});
				} else {
					resolve({
						error: false,
						value: res
					});
				}
			}
		});

	const loadInitial = () =>
		new Promise((resolve, reject) => {
			loading.setLoading(true, 'Cargando, espere por favor...');
			loadAjax({}, 'alumno/alu_automatriculamodulos', 'GET')

				.then((response) => {
					if (response.value.isSuccess) {
						data = response.value.data;
						resolve({
							error: false,
							value: true
						});
					} else {
						is_error = true;
						message_error = response.value.message
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
					is_error = true;
					message_error = error.message
					reject({
						error: true,
						message: error.message
					});
				});
			loading.setLoading(false, 'Cargando, espere por favor...');
		});

	const nextProccess = (value) => {
		if (value == 1) {
			loadInitial();
		}
	};

	const actionRun = (event) => {
		mOpenModalGenerico = false;
		mOpenOffCanvasGenerico = false;
		const detail = event.detail;
		const action = detail.action;
		const value = detail.value;
		if (action == 'nextProccess') {
			loading.setLoading(false, 'Cargando, espere por favor...');
			nextProccess(value);
		}
	};

</script>

<!-- mis componentes -->

<svelte:head>
	<title>Matriculación módulos inglés</title>
</svelte:head>
<BreadCrumb title="MATRICULACIÓN MÓDULOS DE INGLÉS" items={itemsBreadCrumb} back={backBreadCrumb} />

{#if !is_error}
	{#if !load}
		<PanelMatricula {data} on:actionRun={actionRun}></PanelMatricula>
	{:else}
		<div
				class="m-0 vh-100 row justify-content-center align-items-center"
				style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
		>
			<div class="col-auto text-center">
				<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;"/>
				<h3>Verificando la información, espere por favor...</h3>
			</div>
		</div>
	{/if}

{:else}
	<ModuleError title="Matriculación Módulos de inglés" message={message_error}/>
{/if}




{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
		on:actionRun={actionRun}
	/>
{/if}

{#if mOpenOffCanvasGenerico}
	<OffCanvasGenerico
		mToggle={mToggleOffCanvasGenerico}
		mOpen={mOpenOffCanvasGenerico}
		OffCanvasContent={modalDetalleOffCanvasContent}
		aData={aDataModal}
		placement={aplacement}
		{modalTitle}
		on:actionRun={actionRun}
	/>
{/if}

<style>
	/* 	CSS variables can be used to control theming.
			https://github.com/rob-balfre/svelte-select/blob/master/docs/theming_variables.md
	*/

	.propiedades {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 1000;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}
	form {
		/*max-width: 400px;*/
		background: #f4f4f4;
		padding: 0;
		border-radius: 4px;
	}

	label {
		margin: 0 0 10px;
	}
	.themed {
		--border: 3px solid blue;
		--borderRadius: 10px;
		--placeholderColor: blue;
	}
</style>
