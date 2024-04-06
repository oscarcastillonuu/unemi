<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Mi malla académica';
		let ePersona = {};
		let eInscripcion = {};
		let eMalla = {};
		let eAsignaturasMalla = [];

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			//const dataSession = JSON.parse(ds);
			const [res, errors] = await apiGET(fetch, 'alumno/malla', {});
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					if (!res.module_access) {
						return {
							status: 302,
							redirect: '/'
						};
					}
				} else {
					//console.log(res.data);
					Title = res.data.Title;
					eInscripcion = res.data.eInscripcion;
					ePersona = eInscripcion.persona;
					eMalla = res.data.eMalla;
					eAsignaturasMalla = res.data.eAsignaturasMalla;
				}
			}
		} else {
			return {
				status: 302,
				redirect: '/login'
			};
		}

		return {
			props: {
				Title,
				ePersona,
				eInscripcion,
				eMalla,
				eAsignaturasMalla
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
	import { Icon, Spinner } from 'sveltestrap';
	import ComponenteDetallePrecedencia from './_componentePrecedencias.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	export let Title;
	export let ePersona;
	export let eInscripcion;
	export let eMalla;
	export let eAsignaturasMalla;
	let itemsBreadCrumb = [{ text: 'Mi malla', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	let modalSize = 'xl';
	let load = true;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (ePersona) {
			load = false;
		}
	});

	const loadPrecedencias = (eAsignaturaMalla) => {
		aDataModal = { predecesoras: eAsignaturaMalla.predecesoras };
		modalDetalleContent = ComponenteDetallePrecedencia;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = `Precedencias de la asignatura ${eAsignaturaMalla.asignatura.nombre}`;
		modalSize = 'lg';
	};
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>
{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="py-1 py-lg-1">
		<div class="container">
			<div class="row mb-10 justify-content-center">
				<div class="col-lg-8 col-md-12 col-12 text-center">
					<!-- caption -->
					<span class="text-info mb-3 d-block text-uppercase fw-semi-bold ls-xl"
						>{ePersona.nombre_completo}</span
					>
					<h2 class="mb-2 display-4 fw-bold ">{eMalla.carrera.nombre}</h2>
					<p class="lead">MODALIDAD {eMalla.modalidad.nombre} ({eMalla.fecha_display})</p>
				</div>
			</div>
		</div>
	</div>
	{#if eMalla.niveles && eMalla.niveles.length > 0}
		<div class="row">
			<div class="col-12">
				<div class="table-responsive">
					<table class="table table-bordered align-middle table-sm">
						<thead class="">
							<tr class="">
								<th scope="col" class="table-secondary text-center fs-6">Eje formativo</th>
								{#each eMalla.niveles as eNivel}
									<th scope="col" class="table-secondary text-center fs-6 align-middle"
										>{eNivel.nombre}</th
									>
								{/each}
							</tr>
						</thead>
						<tbody>
							{#each eMalla.ejesformativos as eEjeFormativo}
								<tr>
									<th scope="row" class="fs-6">{eEjeFormativo.nombre}</th>
									{#each eMalla.niveles as eNivel}
										<td class="fs-6 text-center">
											{#each eAsignaturasMalla as eAsignaturaMalla}
												{#if eAsignaturaMalla.nivelmalla.id === eNivel.id && eAsignaturaMalla.ejeformativo.id === eEjeFormativo.id}
													<div
														class="card h-100 p-2 mb-2 {eAsignaturaMalla.recordacademico
															? eAsignaturaMalla.recordacademico.aprobada
																? 'bg-success text-white'
																: 'bg-danger text-white'
															: ''}"
													>
														<div
															class="card-header p-2 {eAsignaturaMalla.recordacademico
																? eAsignaturaMalla.recordacademico.aprobada
																	? 'bg-success text-white'
																	: 'bg-danger text-white'
																: ''}"
														>
															<span class="fw-bold ">{eAsignaturaMalla.asignatura.nombre}</span>
														</div>
														<div class="card-body p-2">
															{#if eAsignaturaMalla.recordacademico}
																<div class="d-flex justify-content-between mt-0 fs-6">
																	<span>Nota:</span>
																	<span class="fw-bold"
																		>{eAsignaturaMalla.recordacademico.nota}</span
																	>
																</div>
																{#if !eAsignaturaMalla.recordacademico.sinasistencia}
																	<div class="d-flex justify-content-between mt-0 fs-6">
																		<span>Asistencia:</span>
																		<span class="fw-bold"
																			>{eAsignaturaMalla.recordacademico.asistencia}%</span
																		>
																	</div>
																{/if}
															{/if}
															<div class="d-flex justify-content-between mt-0 fs-6">
																<span>Créditos:</span>
																<span class="fw-bold">{eAsignaturaMalla.creditos}</span>
															</div>
															{#if eAsignaturaMalla.predecesoras.length > 0}
																<div class="d-flex justify-content-between mt-0 fs-6">
																	<span>Precedencias:</span>
																	<button
																		type="button"
																		class="btn btn-primary btn-sm p-0 m-0"
																		on:click={() => loadPrecedencias(eAsignaturaMalla)}
																		><Icon name="info" /></button
																	>
																</div>
															{/if}
															{#if eAsignaturaMalla.itinerario > 0}
																<div class="d-flex justify-content-between mt-0 fs-6">
																	<span>Itinerario:</span>
																	<span class="fw-bold">{eAsignaturaMalla.itinerario}</span>
																</div>
															{/if}
														</div>
													</div>
												{/if}
											{/each}
										</td>
									{/each}
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	{/if}
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
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size={modalSize}
	/>
{/if}

<style>
</style>
