<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: Load = async ({ fetch }) => {
		let eMatriculaSedeExamen = {};
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/aulavirtual', {
				action: 'loadDataArchivoIdentidad'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					}
				} else {
					eMatriculaSedeExamen = res.data['eMatriculaSedeExamen'];
				}
			}
		}

		return {
			props: {
				eMatriculaSedeExamen
			}
		};
	};
</script>

<script>
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { Spinner } from 'sveltestrap';
	import ComponentStep_1 from './_step_1/index.svelte';
	import ComponentStep_2 from './_step_2/index.svelte';
	import { addToast } from '$lib/store/toastStore';
	import { apiPOST, browserGet } from '$lib/utils/requestUtils';
	export let eMatriculaSedeExamen;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let itemsBreadCrumb = [
		{ text: 'Aula Virtual', active: false, href: '/alu_documentos' },
		{ text: 'Verificación de identidad', active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/alu_documentos', text: 'Atrás' };
	let step_1 = true,
		step_2 = false;
	let load = true;
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		if (eMatriculaSedeExamen) {
			const tiene_paso_1 = eMatriculaSedeExamen.tiene_paso_1 ?? false;
			const tiene_paso_2 = eMatriculaSedeExamen.tiene_paso_2 ?? false;
			if (tiene_paso_1) {
				await changeStep(2);
				step_1 = false;
				step_2 = true;
			} else if (tiene_paso_2) {
				goto('/alu_documentos');
			}
		}
		await delay(2000);
		load = false;
	});

	const actionRun = async (event) => {
		// console.log(event.detail);
		const detail = event.detail;
		const action = detail.action;
		const next = detail.next;
		const previous = detail.previous;
		const aData = detail.aData;
		if (action == 'changeStep') {
			if (next == 1 && previous == 1) {
				await changeStep(next);
				step_1 = true;
				step_2 = false;
			} else if (next == 2 && previous == 1) {
				await changeStep(next);
				step_1 = false;
				step_2 = true;
				if (aData) {
					eMatriculaSedeExamen = { ...aData.eMatriculaSedeExamen };
					console.log(eMatriculaSedeExamen);
				}
			} else if (next == null && previous == 2) {
				await changeStep(next);
				step_2 = true;
			}
		}
	};

	const changeStep = async (step) => {
		const stepId = document.getElementById(`btn-step-${step}`);
		const classStepPan = document.querySelectorAll('.bs-stepper-pane');
		const classStep = document.querySelectorAll('.step');
		const controls = `step-${step}`;
		classStepPan.forEach((element, index, array) => {
			element.classList.remove('active');
			element.classList.remove('dstepper-block');
			element.classList.add('dstepper-none');
			//element.style.display = 'none';
		});
		classStep.forEach((element, index, array) => {
			element.classList.remove('active');
		});
		const dataTarget = document.querySelectorAll(`[data-target="#step-${step}"]`);
		if (dataTarget) {
			dataTarget.forEach((element) => {
				element.classList.add('active');
			});
		}

		const stepPanID = document.getElementById(`step-${step}`);
		if (stepPanID) {
			stepPanID.classList.remove('dstepper-none');
			stepPanID.classList.add('active');
			stepPanID.classList.add('dstepper-block');
		}
		//stepPanID.style.display = 'block';
	};
</script>

<BreadCrumb title={undefined} items={itemsBreadCrumb} back={backBreadCrumb} />
<svelte:head>
	<title>Aula Virtual | Verificación de identidad</title>
</svelte:head>

{#if !load}
	<div class="container">
		<div id="" class="bs-stepper">
			<div class="row">
				<div class="offset-lg-1 col-lg-10 col-md-12 col-12">
					<div class="bs-stepper-header" style="display: none;" role="tablist">
						<div class="step active" data-target="#step-1">
							<button
								type="button"
								class="step-trigger {step_1 ? 'active' : 'disabled'}"
								role="tab"
								id="btn-step-1"
								aria-controls="step-1"
								aria-selected="true"
								on:click={() => changeStep(1)}
							>
								<span class="bs-stepper-circle">1</span>
								<span class="bs-stepper-label">Paso</span>
							</button>
						</div>
						<div class="bs-stepper-line" />
						<div class="step" data-target="#step-2">
							<button
								type="button"
								class="step-trigger {step_2 ? 'active' : 'disabled'}"
								role="tab"
								id="btn-step-2"
								aria-controls="step-1"
								aria-selected="false"
								on:click={() => changeStep(2)}
							>
								<span class="bs-stepper-circle">2</span>
								<span class="bs-stepper-label">Paso</span>
							</button>
						</div>
					</div>
					<div class="bs-stepper-content">
						<div
							id="step-1"
							role="tabpanel"
							class="bs-stepper-pane fade {step_1 ? 'dstepper-block active' : 'dstepper-none'}"
							aria-labelledby="btn-step-1"
						>
							<svelte:component
								this={ComponentStep_1}
								{eMatriculaSedeExamen}
								on:actionRun={actionRun}
							/>
						</div>
						<div
							id="step-2"
							role="tabpanel"
							class="bs-stepper-pane fade {step_2 ? 'dstepper-block active' : 'dstepper-none'}"
							aria-labelledby="btn-step-2"
						>
							<svelte:component
								this={ComponentStep_2}
								{eMatriculaSedeExamen}
								on:actionRun={actionRun}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
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
