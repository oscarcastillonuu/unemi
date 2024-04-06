<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Mi carné estudiantil';
		let eMatricula = {};
		let eCarnet = {};
		let eConfiguracionCarnet = {};
		let ePersona = {};
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Eliminando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/carnet', {});
			loading.setLoading(false, 'Eliminando, espere por favor...');
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
									redirect: `/`
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
					//console.log(res.data);
					Title = res.data.Title;
					eMatricula = res.data.eMatricula;
					eCarnet = res.data.eCarnet;
					eConfiguracionCarnet = res.data.eConfiguracionCarnet;
					ePersona = eMatricula.persona;
					if (!ePersona.tiene_foto) {
						return {
							status: 302,
							redirect: '/alu_carnet/foto'
						};
					}
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
				eMatricula,
				eCarnet,
				eConfiguracionCarnet,
				ePersona
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount, onDestroy } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { Icon, Spinner } from 'sveltestrap';
	import ModalGenerico from '$components/Alumno/Modal.svelte';

	const DEBUG = import.meta.env.DEV;
	export let Title = 'Mi carné estudiantil';
	export let eMatricula;
	export let eCarnet;
	export let eConfiguracionCarnet;
	export let ePersona;
	let load = true;
	let itemsBreadCrumb = [{ text: 'Mi carné estudiantil', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (eMatricula) {
			load = false;
		}
	});

	onDestroy(() => {});

	const printCarnet = (url) => {
		window.open(`${url}`, '_blank');
	};

	const eliminarCarnet = async (id) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted eliminara el carné estudiantil. ¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de eliminar carné estudiantil?`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Si, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Eliminando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/carnet', {
						action: 'deleteCarnet',
						id: id
					});
					loading.setLoading(false, 'Eliminando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						goto('/');
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se elimino correctamente el carné estudiantil'
							});
							goto('/');
						}
					}
				} else {
					addToast({
						type: 'info',
						header: 'Enhorabuena',
						body: 'Has cancelado la acción de eliminar carnet'
					});
				}
			})
			.catch((error) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: error });
			});
	};
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>
{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="py-lg-0">
		<div class="container px-4 px-lg-8">
			<div class="row">
				<div class="col-12">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						{#if eCarnet && eCarnet.pdf}
							<button
								class="btn btn-secondary btn-sm me-md-2"
								on:click|preventDefault={() => printCarnet(eCarnet.pdf)}
								type="button">Imprimir PDF</button
							>
						{/if}
						{#if eConfiguracionCarnet.puede_subir_foto}
							<button
								class="btn btn-success btn-sm me-md-2"
								on:click|preventDefault={() => goto('/alu_carnet/foto')}
								type="button">Cambiar foto</button
							>
						{/if}
						{#if eMatricula && eConfiguracionCarnet.puede_eliminar_carne}
							<button
								class="btn btn-warning btn-sm me-md-2"
								on:click|preventDefault={() => eliminarCarnet(eMatricula.id)}
								type="button">Volver a generar carnet</button
							>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
	{#if eCarnet}
		<div class="py-lg-2">
			<div class="container px-4 px-lg-0">
				<div class="row">
					<div class="offset-lg-2 col-lg-8 col-12">
						<div class="bg-light py-10 px-8 rounded-3">
							<div class="row align-items-center">
								<div class="col-12">									
									<iframe class="rounded-top-md" src="{eCarnet.pdf}" frameborder="0" height="400px" width="100%">
									
									</iframe>
								</div>								
							</div>
							<!-- <div class="row align-items-center">
								{#if eConfiguracionCarnet.es_anverso}
									<div class="col-12">
										<img class="rounded-top-md img-fluid" src={eCarnet.png_anverso} alt="" />
									</div>
								{:else if eConfiguracionCarnet.es_reverso}
									<div class="col-12">
										<img class="rounded-top-md img-fluid" src={eCarnet.png_reverso} alt="" />
									</div>
								{:else}
									<div class="col-lg-6 col-12">
										<img class="rounded-top-md img-fluid" src={eCarnet.png_anverso} alt="" />
									</div>
									<div class="col-lg-6 col-12">
										<img class="rounded-top-md img-fluid" src={eCarnet.png_reverso} alt="" />
									</div>
								{/if}
							</div> -->
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
{:else}
	<div
		class="mt-4 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
