<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Hoja de vida';
		let ePersona = {};
		let messageError = undefined;
		let isError = false;

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const [res, errors] = await apiGET(fetch, `alumno/hoja_vida`, {
				action: 'loadDatosPersonales'
			});
			if (errors.length > 0) {
				isError = true;
				messageError = errors[0].error;
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'warning', header: 'Advertencia', body: res.message });
					isError = true;
					messageError = res.message;
				} else {
					ePersona = res.data.ePersona;
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
	import ComponenteDatosPersonales from './_componentes/informacion_personal/datos_personales/index.svelte';
	import ComponenteDatosPersonalesEtnia from './_componentes/informacion_personal/datos_etnia/index.svelte';
	import ComponenteDatosPersonalesMigrante from './_componentes/informacion_personal/datos_migrante/index.svelte';
	import ComponenteDatosMedicos from './_componentes/informacion_medica/datos_medicos/index.svelte';
	import ComponenteDatosDiscapacidad from './_componentes/informacion_medica/discapacidad/index.svelte';
	import ComponenteDatosEmbarazo from './_componentes/informacion_medica/embarazo/index.svelte';
	import ComponenteMisTitulos from './_componentes/informacion_academica/mis_titulos/index.svelte';
	import ComponenteMisCapacitaciones from './_componentes/informacion_academica/mis_capacitaciones/index.svelte';
	import ComponenteMisCertificaciones from './_componentes/informacion_academica/mis_certificaciones/index.svelte';
	import ComponenteDatosArtista from './_componentes/deporte_cultura/artista/index.svelte';
	import ComponenteDatosDeportista from './_componentes/deporte_cultura/deportista/index.svelte';
	import ComponenteDatosProyectos from './_componentes/informacion_academica/proyectos/index.svelte';
	import ComponenteDatosBecas from './_componentes/informacion_academica/becas/index.svelte';
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
	export let messageError;
	export let isError;
	let itemsBreadCrumb = [{ text: 'Hoja de vida', active: false, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let componentContent;
	let componentData;
	//console.log($navigating);
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (ePersona) {
			load = false;
			componentData = { ePersona: ePersona };
			componentContent = ComponenteDatosPersonales;
		} else {
			load = false;
			componentData = await actionLoadInformation('loadDatosPersonales');
			componentContent = ComponenteDatosPersonales;
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
		const [res, errors] = await apiGET(fetch, 'alumno/hoja_vida', {
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
			// console.log(item);
			componentContent = undefined;
			if (item === 1) {
				componentData = await actionLoadInformation('loadDatosPersonales');
				componentContent = ComponenteDatosPersonales;
			} else if (item === 2) {
				componentData = await actionLoadInformation('loadDatosPersonalesEtnia');
				componentContent = ComponenteDatosPersonalesEtnia;
			} else if (item === 3) {
				componentData = await actionLoadInformation('loadDatosPersonalesMigrante');
				componentContent = ComponenteDatosPersonalesMigrante;
			} else if (item === 4) {
				componentData = await actionLoadInformation('loadDatosPersonalesMedicos');
				componentContent = ComponenteDatosMedicos;
			} else if (item === 5) {
				componentData = await actionLoadInformation('loadDatosPersonalesDiscapacidad');
				componentContent = ComponenteDatosDiscapacidad;
			} else if (item === 6) {
				componentData = await actionLoadInformation('loadDatosPersonalesEmbarazo');
				componentContent = ComponenteDatosEmbarazo;
			} else if (item === 7) {
				componentData = await actionLoadInformation('loadFormacionAcademicaMisTitulos');
				componentContent = ComponenteMisTitulos;
			} else if (item === 8) {
				componentData = await actionLoadInformation('loadFormacionAcademicaMisCapacitaciones');
				componentContent = ComponenteMisCapacitaciones;
			} else if (item === 9) {
				componentData = await actionLoadInformation('loadFormacionAcademicaMisCertificaciones');
				componentContent = ComponenteMisCertificaciones;
			} else if (item === 10) {
				componentData = await actionLoadInformation('loadDeporteCulturaArtistas');
				componentContent = ComponenteDatosArtista;
			} else if (item === 11) {
				componentData = await actionLoadInformation('loadDeporteCulturaDeportistas');
				componentContent = ComponenteDatosDeportista;
			} else if (item === 12) {
				componentData = await actionLoadInformation('loadFormacionAcademicaProyectos');
				componentContent = ComponenteDatosProyectos;
			} else if (item === 13) {
				componentData = await actionLoadInformation('loadFormacionAcademicaBecas');
				componentContent = ComponenteDatosBecas;
			}
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
	};
</script>

<!--https://geeksui.codescandy.com/geeks/pages/student-subscriptions.html#-->
<svelte:head>
	<title>{Title}</title>
</svelte:head>

{#if !load}
	{#if !isError}
		<BreadCrumb
			title="Hoja de vida"
			subtitle="Gestiona tu información y mejora tu experiencia"
			items={itemsBreadCrumb}
			back={backBreadCrumb}
		/>
		<div class="container-fluid">
			<div class="row ">
				<div class="col-lg-3 col-md-4 col-12 ">
					<Menu on:actionRun={actionRun} {ePersona} />
				</div>
				<div class="col-lg-9 col-md-8 col-12 ">
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
