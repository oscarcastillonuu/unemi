<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';
	import GridIdiomas  from './grid_idioma.svelte'
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
	export const load: Load = async ({ fetch }) => {
		let ePeriodo = [];
		let mis_gruposInscripcion = [];
		let idiomas = [];
		let cursa_modulo_de_ingles = false;
		let cupos_disponible = 0;
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/idiomas', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: errors[0].error
				});
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
				} else {
					console.log(res.data);
					ePeriodo = res.data['ePeriodo'];
					mis_gruposInscripcion = res.data['mis_gruposInscripcion'];
					cursa_modulo_de_ingles = res.data['cursa_modulo_de_ingles'];
					cupos_disponible = res.data['cupos_disponible'];
					idiomas = res.data['idiomas'];

				}
			}
		}
		return {
			props: {
				ePeriodo,
				mis_gruposInscripcion,
				cursa_modulo_de_ingles,
				cupos_disponible,
                idiomas

			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import Swal from 'sweetalert2';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import OffCanvasGenerico from '$components/Alumno/OffCanvasModal.svelte';
	import { addNotification } from '$lib/store/notificationStore';
	import ModalModulosHomologados from './_modalModuloHomologados.svelte';
	import ModalTablaCalificacion from './_tablacalificaciones.svelte';
	let aDataModal = {};
	let aplacement = '';
	let modalDetalleOffCanvasContent;
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenOffCanvasGenerico = false;
	let modalTitle = '';
	export let ePeriodo;
	export let mis_gruposInscripcion;
	export let cursa_modulo_de_ingles;
	export let cupos_disponible;
	export let idiomas;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	const mToggleOffCanvasGenerico = () => (mOpenOffCanvasGenerico = !mOpenOffCanvasGenerico);
	let itemsBreadCrumb = [
		{
			text: 'Prueba ubicación de idiomas',
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
			loadAjax({}, 'alumno/idiomas', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						ePeriodo= response.value.data['ePeriodo'];
						mis_gruposInscripcion= response.value.data['mis_gruposInscripcion'];
						cursa_modulo_de_ingles= response.value.data['cursa_modulo_de_ingles'];
						cupos_disponible= response.value.data['cupos_disponible'];
						idiomas= response.value.data['idiomas'];

						resolve({
							error: false,
							value: true
						});
					} else {
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
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

	const loadModalModulosHomologados = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiGET(fetch, 'alumno/idiomas', {
			action: 'loadModulosHomologados',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				aDataModal = res.data;
				modalDetalleContent = ModalModulosHomologados;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'INFORMACIÓN';
			}
		}
	};

	const loadTablaHomologar = async (id) => {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/idiomas', {
				action: 'loadTablaHomologar',
				id: id
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addNotification({
					msg: errors[0].error,
					type: 'error'
				});
			} else {
				if (!res.isSuccess) {
					addNotification({
						msg: res.message,
						type: 'error'
					});
				} else {
					aDataModal = res.data;
					modalDetalleContent = ModalTablaCalificacion;
					mOpenModalGenerico = !mOpenModalGenerico;
					modalTitle = 'INFORMACIÓN DE TABLA DE RANGO DE CALIFICACIONES.';
				}
			}
		};

</script>

<!-- mis componentes -->

<svelte:head>
	<title>Prueba ubicación de idiomas</title>
</svelte:head>
<BreadCrumb title="PRUEBA UBICACIÓN DE IDIOMAS" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="container-fluid">
	<div class="container-fluid">
		<h2 class="text">Mis inscripciones</h2>
		<div class="row mb-4">
			<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
			<thead class="table-ligth">
			<tr>
				<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Grupo</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Fecha</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Día</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Horarios</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Estado</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Acceso</th>
			</tr>
			</thead>
			<tbody>
				{#each mis_gruposInscripcion as mi_grupo, index}
					<tr>
						<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{index+1}
						</td>
						<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{mi_grupo.grupo.display}
						</td>
						<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{mi_grupo.grupo.fecinicio}
						</td>
						<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{mi_grupo.grupo.inicio_display}
						</td>
						<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{mi_grupo.grupo.horario}
						</td>
						<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{#if mi_grupo.estado === 0}  <span
									class="badge bg-warning">{mi_grupo.estado_display}</span>{/if}
							{#if mi_grupo.estado === 1}  <span
									class="badge bg-success">{mi_grupo.estado_display}</span>{/if}
							{#if mi_grupo.estado === 2}  <span
									class="badge bg-danger">{mi_grupo.estado_display}</span>{/if}
							<br>
							{#if mi_grupo.estado != 0} <span class="badge bg-primary"><b>Nota:</b> {mi_grupo.nota}</span> {/if}

						</td>
                        <td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
							{#if mi_grupo.grupo.existe_curso_moodle === true}
								{#if mi_grupo.grupo.puede_visualizar_url_moodle === true}
									<span class="fs-6 btn badge bt">
										<a href="{mi_grupo.grupo.periodo.url}?id={mi_grupo.grupo.idcursomoodle}" class="btn btn-primary"
												target="_blank"><span class="fe fe-link"/> Ir al curso</a>
									</span>
								{:else}

									{#if mi_grupo.estado === 1}
                                          <button on:click|preventDefault={() => loadModalModulosHomologados(mi_grupo.id)} class="btn btn-info  btn-sm  rounded-pill text-white" type="button">
                                            Ver módulos homologados
                                        </button>
									{:else}
										<button on:click|preventDefault={() => loadTablaHomologar(mi_grupo.id)} class="btn btn-info  btn-sm  rounded-pill text-white" type="button">
                                            Ver
                                        </button>
									{/if}
								{/if}
							{:else}
								{#if mi_grupo.grupo.periodo.url }
									<a href="{mi_grupo.grupo.periodo.url}" class="btn btn-primary" target="_blank"><span class="fe fe-link"/> Ir al curso</a>
								{:else}
									<span class="badge bg-warning  ">No disponible</span>
								{/if}
							{/if}
						</td>
					</tr>
				{:else}
					<tr>
						<td>No se ha inscrito en ningun grupo</td>
					</tr>
				{/each}
			</tbody>
		</table>
		</div>
	</div>
</div>

<div class="row">
	<div class="alertas_idioma_ingles">
		{#if cursa_modulo_de_ingles}
		<Alert color="danger">Lamentamos informarte que no puedes inscribirte en las pruebas de suficiencia de Inglés en este momento, ya que al haber aprobado al menos un módulo, no cumples con los requisitos necesarios para la inscripción, los cuales establecen que no debes tener ningún módulo aprobado previamente.</Alert>
		<h4 class="fw-bold">En cumplimiento al Artículo 112 .- Aprendizaje de una segunda lengua.</h4>
		<Alert color="info">La prueba de ubicación de inglés, se tomará por una sola vez al inicio del estudio de la
			asignatura de inglés de cada estudiante. La calificación obtenida en la prueba de ubicación de inglés
			determinará el nivel en el que el estudiante deberán matricularse.
		</Alert>
	{/if}
	</div>

</div>

<div class="container-fluid">
	{#if  ePeriodo == null || ePeriodo.length != 0  }
			{#key mis_gruposInscripcion}
				<GridIdiomas idiomas = {idiomas} cursa_modulo_de_ingles = {cursa_modulo_de_ingles} ePeriodo={ePeriodo} mis_gruposInscripcion = {mis_gruposInscripcion} on:actionRun={actionRun}>
				</GridIdiomas>
			{/key}
	{:else }
			<div class="mt-4 vh-100 row justify-content-center align-items-center propiedades" >
				<div class="col-auto text-center">
					<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;"/>
					<h3>Verificando la información, espere por favor...</h3>
				</div>
			</div>
	{/if}

</div>





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
