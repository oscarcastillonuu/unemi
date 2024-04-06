<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Encuesta de Estratificación del Nivel Socioeconómico';
		let ePersona = {};
		let eInscripcion = {};
		let eCarrera = {};
		let messageError = undefined;
		let isError = false;

		const ds = browserGet('dataSession');
		console.log(ds);
		if (ds != null || ds != undefined) {
			/*const dataSession = JSON.parse(ds);
			const inscripcion = dataSession['inscripcion'];
			const id = inscripcion['id'];*/
			const [res, errors] = await apiGET(fetch, `alumno/socioeconomica`, {});
			//console.log(res);
			if (errors.length > 0) {
				//addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				isError = true;
				messageError = errors[0].error;
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'warning', header: 'Advertencia', body: res.message });
					isError = true;
					messageError = res.message;
				} else {
					//console.log(res.data);
					//Title = res.data.Title;
					eInscripcion = res.data.eInscripcion;
					ePersona = eInscripcion.persona;
					eCarrera = eInscripcion.carrera;
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
				eInscripcion,
				ePersona,
				eCarrera,
				isError,
				messageError
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import { decodeToken } from '$lib/utils/decodetoken';
	import type { Coordinacion } from '$lib/interfaces/user.interface';
	import {
		browserGet,
		apiPOST,
		apiGET,
		getCurrentRefresh,
		browserSet
	} from '$lib/utils/requestUtils';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModuleError from './_error.svelte';
	import Menu from './_menu.svelte';
	import ComponenteDatosPersonales from './_componentes/datos_personales/index.svelte';
	import ComponenteDatosFamiliares from './_componentes/datos_familiares/index.svelte';
	import ComponenteDiscapacidad from './_componentes/discapacidad/index.svelte';
	import ComponenteNacimiento from './_componentes/datos_nacimiento/index.svelte';
	import ComponenteDomicilio from './_componentes/datos_domicilio/index.svelte';
	import ComponenteEstructuraFamiliar from './_componentes/estructura_familiar/index.svelte';
	import ComponenteNivelEducacion from './_componentes/nivel_educacion/index.svelte';
	import ComponenteCaracteristicaVivienda from './_componentes/caracteristicas_vivienda/index.svelte';
	import ComponenteHabitoConsumo from './_componentes/habitos_consumo/index.svelte';
	import ComponentePosesionBienes from './_componentes/posesion_bienes/index.svelte';
	import ComponenteAccesoTecnologia from './_componentes/acceso_tecnologia/index.svelte';
	import ComponenteInstalaciones from './_componentes/instalaciones/index.svelte';
	import ComponenteActividadesExtracurriculares from './_componentes/actividades_extracurriculares/index.svelte';
	import ComponenteRecursosEstudio from './_componentes/recursos_estudio/index.svelte';
	import ComponenteSaludEstudiante from './_componentes/salud_estudiante/index.svelte';
	import ComponenteDatosEtnia from './_componentes/datos_etnia/index.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import { Spinner } from 'sveltestrap';
	import { addToast } from '$lib/store/toastStore';
	import { userData } from '$lib/store/userStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { goto } from '$app/navigation';
	import Swal from 'sweetalert2';

	export let Title;
	export let ePersona;
	export let eInscripcion;
	export let eCarrera;
	export let messageError;
	export let isError;
	let itemsBreadCrumb = [
		{ text: 'Encuesta de Nivel Socioeconómico', active: false, href: undefined }
	];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let componentContent;
	let componentData;
	//console.log($navigating);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (eInscripcion && ePersona && eCarrera) {
			load = false;
			componentData = await actionLoadInformation('loadDatosPersonales');
			componentContent = ComponenteDatosPersonales;
			// console.log("componentData: ", componentData)
		}
	});

	const actionLoadInformation = async (action) => {
		if (browserGet('refreshToken')) {
			const response = await getCurrentRefresh(fetch, `${variables.BASE_API_URI}/token/refresh`);
			if (response.status >= 400) {
				goto('/lock-screen');
			}
			if (response.ok == true) {
				const json = decodeToken(await response.json());
				browserSet('refreshToken', json.tokens.refresh);
				browserSet('accessToken', json.tokens.access);
				browserSet('dataSession', JSON.stringify(json));
				userData.set(json);
			}
		} else {
			goto('/login');
		}
		let aData = {};
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
			action: action
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
				// console.log(res.data);
				aData = { ...res.data };
			}
		}
		return aData;
	};

	const actionRun = async (event) => {
		const detail = event.detail;
		const action = detail.action;
		const data = detail.data;

		if (action == 'selectItem') {
			loading.setLoading(true, 'Cargando, espere por favor...');
			// closeModal();
			// console.log(action);
			// console.log(data);
			const item = data.item;
			componentContent = undefined;
			if (item === 1) {
				componentData = await actionLoadInformation('loadDatosPersonales');
				componentContent = ComponenteDatosPersonales;
			} else if (item === 2) {
				componentData = await actionLoadInformation('loadDatosFamiliares');
				componentContent = ComponenteDatosFamiliares;
			} else if (item === 3) {
				componentData = await actionLoadInformation('loadDatosDiscapacidad');
				componentContent = ComponenteDiscapacidad;
			} else if (item === 4) {
				componentData = await actionLoadInformation('loadDatosNacimiento');
				componentContent = ComponenteNacimiento;
			} else if (item === 5) {
				componentData = await actionLoadInformation('loadDatosDomicilio');
				componentContent = ComponenteDomicilio;
			} else if (item === 6) {
				componentData = await actionLoadInformation('loadDatosEstructuraFamiliar');
				componentContent = ComponenteEstructuraFamiliar;
			} else if (item === 7) {
				componentData = await actionLoadInformation('loadDatosNivelEducacion');
				componentContent = ComponenteNivelEducacion;
			} else if (item === 8) {
				componentData = await actionLoadInformation('loadDatosCaracteristicasVivienda');
				componentContent = ComponenteCaracteristicaVivienda;
			} else if (item === 9) {
				componentData = await actionLoadInformation('loadDatosHabitosConsumo');
				componentContent = ComponenteHabitoConsumo;
			} else if (item === 10) {
				componentData = await actionLoadInformation('loadDatosPosesionBienes');
				componentContent = ComponentePosesionBienes;
			} else if (item === 11) {
				componentData = await actionLoadInformation('loadDatosAccesosTecnologia');
				componentContent = ComponenteAccesoTecnologia;
			} else if (item === 12) {
				componentData = await actionLoadInformation('loadDatosInstalaciones');
				componentContent = ComponenteInstalaciones;
			} else if (item === 13) {
				componentData = await actionLoadInformation('loadDatosActividadesExtracurriculares');
				componentContent = ComponenteActividadesExtracurriculares;
			} else if (item === 14) {
				componentData = await actionLoadInformation('loadDatosRecursosEstudio');
				componentContent = ComponenteRecursosEstudio;
			} else if (item === 15) {
				componentData = await actionLoadInformation('loadDatosSaludEstudiante');
				componentContent = ComponenteSaludEstudiante;
			} else if (item === 16) {
				componentData = await actionLoadInformation('loadDatosPersonalesEtnia');
				componentContent = ComponenteDatosEtnia;

			}
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
	};

	const actionSaveConfirmar = async () => {
		const mensaje = {
			title: `Encuesta de Estratificación del Nivel Socioeconómico`,
			html: `¿Está seguro/a de confirmar la encuesta?`,
			type: 'info',
			icon: 'info',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Si`,
			cancelButtonText: 'No'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Procesando la información, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
						action: 'saveConfirmar'
					});
					loading.setLoading(false, 'Procesando la información, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						loading.setLoading(false, 'Cargando, espere por favor...');
						return;
					} else {
						loading.setLoading(false, 'Cargando, espere por favor...');
						if (!res.isSuccess) {
							if (res.data['errors']) {
								addToast({
									type: 'error',
									header: `${res.message}`,
									body: `${res.data['errors']}`
								});
							} else {
								addToast({ type: 'error', header: '¡ERROR!', body: res.message });
							}
							return;
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se confirmo correctamente los datos'
							});
							goto('/');
						}
					}
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena puedes seguir editando la encuesta',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};
</script>

<!--https://geeksui.codescandy.com/geeks/pages/student-subscriptions.html#-->
<svelte:head>
	<title>{Title}</title>
</svelte:head>
{#if !load}
	{#if !isError}
		<BreadCrumb items={itemsBreadCrumb} />
		<div class="container-fluid">
			<div class="row align-items-center">
				<div class="col-xl-12 col-lg-12 col-md-12 col-12">
					<!--<div
						class="pt-16 rounded-top"
						style="background: url(./assets/images/background/profile-bg.jpg) no-repeat; background-size: cover;"
					/>-->

					<div class="row align-items-center mb-5">
						<div class="col-xl-12 col-lg-12 col-md-12 col-12 text-center">
							<h1 class="text-primary fw-bold">
								Encuesta de Estratificación del Nivel Socioeconómico
							</h1>
							<p class="mb-0">
								Texto tomado del Instituto Nacional de Estadísticas y Censos (INEC)
							</p>
						</div>
					</div>
					<div class="d-flex align-items-end justify-content-between mb-5">
						<div class="d-flex align-items-center">
							<div class="me-2 position-relative d-flex justify-content-end align-items-end">
								<img
									src={ePersona.foto_perfil}
									class="avatar-xl rounded-circle border border-4 border-white"
									alt="avatar"
								/>
							</div>
							<div class="lh-1">
								<h2 class="mb-0">{ePersona.nombre_completo}</h2>
								<p class=" mb-0 d-block">{eCarrera.nombre_mostrar}</p>
							</div>
						</div>
						<div>
							<a
								href="javascript:;"
								on:click={actionSaveConfirmar}
								class="btn btn-warning d-none d-md-block">Confirmar</a
							>
						</div>
					</div>
				</div>
			</div>
			<div class="row mt-0 mt-md-4">
				<div class="col-lg-3 col-md-4 col-12">
					<Menu on:actionRun={actionRun} />
				</div>
				<div class="col-lg-9 col-md-8 col-12">
					<svelte:component
						this={componentContent}
						aData={componentData}
						on:actionRun={actionRun}
					/>
				</div>
			</div>
		</div>
	{:else}
		<ModuleError title={Title} message={messageError} />
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
