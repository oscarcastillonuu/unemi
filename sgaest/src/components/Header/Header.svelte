<script lang="ts">
	import {
		browserGet,
		browserSet,
		logOutUser,
		changeProfile,
		apiPOST,
		apiGET,
		loadNotifications
	} from '$lib/utils/requestUtils';
	import { afterUpdate, onDestroy, onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponentChangePassword from '$components/ChangePassword/ChangePassword.svelte';
	import { addToast } from '$lib/store/toastStore';
	import { goto } from '$app/navigation';
	import { pushNotifications } from '$lib/store/pushNotificationStore';
	let eNotificaciones = [];
	let persona = {};
	let perfiles = [];
	let perfilprincipal = {};
	let periodos = [];
	let total_periodos = 0;
	let isLoadPersona = false;
	let periodo = {};
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let modalTitle = '';
	let modalDetalleContent;
	let aDataModal;
	const DEBUG = import.meta.env.DEV;
	onMount(async () => {
		const ds = browserGet('dataSession');

		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			persona = dataSession['persona'];
			isLoadPersona = true;
			const eperfiles = dataSession['perfiles'];

			for (const i in eperfiles) {
				perfiles.push(eperfiles[i]);
			}
			if (perfiles.length > 0) {
				perfiles.sort((a, b) => (a.clasificacion || 0) - (b.clasificacion || 0));
			}

			perfilprincipal = dataSession['perfilprincipal'];
			periodo = dataSession['periodo'];
			const eperiodos = dataSession['periodos'];
			for (const i in eperiodos) {
				periodos.push(eperiodos[i]);
			}
			total_periodos = periodos ? periodos.length : 0;
			await loadNotifications();
			loading.setLoading(false, 'Cargando, espere por favor...');
		}
	});

	onDestroy(() => {
		clearInterval($pushNotifications);
	});

	const closeModal = () => {
		mOpenModalGenerico = false;
	};
	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModal') {
			closeModal();
		}
	};

	const openModalChangePassword = () => {
		aDataModal = {};
		modalDetalleContent = ComponentChangePassword;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = 'Cambiar contraseña';
		aDataModal = { ePersona: persona };
	};

	const gestionarPerfil = () => {
		/*if (DEBUG) {
			goto('/th_hojavida');
		} else {
			const dataSession = JSON.parse(browserGet('dataSession'));
			const connectionToken = dataSession['connectionToken'];
			window.location.href = `${connectionToken}&ret=/th_hojavida`;
		}*/
		goto('/th_hojavida');
	};

	const updateNotificacionView = async (eNotificacion) => {
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			const [res, errors] = await apiPOST(fetch, 'alumno/general/data', {
				action: 'save_view_notifcation_student',
				id: eNotificacion.id
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				logOutUser();
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								if (res.message) {
									addToast({ type: 'warning', header: 'Advertencia', body: res.message });
								}
								logOutUser();
							}
						} else {
							if (res.message) {
								addToast({ type: 'warning', header: 'Advertencia', body: res.message });
							}
							logOutUser();
						}
					} else {
						if (res.message) {
							addToast({ type: 'warning', header: 'Advertencia', body: res.message });
						}
					}
				}
				{
					await loadNotifications();
					goto(`${eNotificacion.url}`);
				}
			}
		}
	};
</script>

<nav class=" navbar navbar-expand-lg navbar-dark bg-sga bg-dark navbar-fixed-top">
	<div class="container-fluid px-0">
		<a
			class="d-none d-sm-block"
			href="/"
			style="vertical-align: middle; font-size: 16px; font-weight: bold;"
		>
			<img src="/sgaplus_white2.svg" alt="" style="height: 40px;" />
		</a>
		<a
			class="d-block d-sm-none"
			href="/"
			style="vertical-align: middle;  font-size: 16px; font-weight: bold;"
		>
			<img src="/sgaplus_white2.svg" alt="" style="height: 1.875rem;" />
		</a>
		<!--Navbar nav -->
		<ul class="navbar-nav navbar-right-wrap ms-auto d-flex nav-top-wrap">
			{#if $pushNotifications}
				<li class="dropdown stopevent d-none d-md-block d-lg-block">
					<a
						class="btn btn-icon rounded-circle text-muted"
						href="/notificacion"
						role="button"
						id="dropdownNotification"
						data-bs-toggle="dropdown"
						aria-haspopup="true"
						aria-expanded="false"
						><span
							class="position-absolute top-20 start-100 translate-middle badge rounded-pill p-1"
							style="background-color: #ffc107 !important;">{$pushNotifications.length}</span
						>
						<i class="fe fe-bell" />
					</a>

					<div
						class="dropdown-menu dropdown-menu-end dropdown-menu-lg"
						aria-labelledby="dropdownNotification"
					>
						<div>
							<div
								class="border-bottom px-3 pb-3 d-flex justify-content-between align-items-center"
							>
								<span class="h4 mb-0">Notificaciones</span>
								<a href="/notificacion" class="text-muted">
									<span class="align-middle">
										<i class="fe fe-settings me-1" />
									</span>
								</a>
							</div>
							<ul
								class="list-group list-group-flush"
								data-simplebar="init"
								style="max-height: 300px;"
							>
								<div class="simplebar-wrapper" style="margin: 0px;">
									<div class="simplebar-height-auto-observer-wrapper">
										<div class="simplebar-height-auto-observer" />
									</div>
									<div class="simplebar-mask">
										<div class="simplebar-offset" style="right: 0px; bottom: 0px;">
											<div
												class="simplebar-content-wrapper"
												tabindex="0"
												role="region"
												aria-label="scrollable content"
												style="height: auto; overflow: hidden;"
											>
												<div class="simplebar-content" style="padding: 0px;">
													{#each $pushNotifications as eNotificacion}
														<li class="list-group-item bg-light">
															<div class="row">
																<div class="col">
																	<a
																		class="text-body"
																		on:click|preventDefault={() =>
																			updateNotificacionView(eNotificacion)}
																	>
																		<div class="d-flex">
																			<!--<img
																		src="../../assets/images/avatar/avatar-1.jpg"
																		alt=""
																		class="avatar-md rounded-circle"
																	/>-->
																			<div class="ms-3">
																				<h5 class="fw-bold mb-1">{eNotificacion.titulo}</h5>
																				<p class="mb-3">
																					{eNotificacion.cuerpo}
																				</p>
																				<!--<span class="fs-6 text-muted">
																			<span
																				><span class="fe fe-thumbs-up text-success me-1" />2 hours
																				ago,</span
																			>
																			<span class="ms-1">2:19 PM</span>
																		</span>-->
																			</div>
																		</div>
																	</a>
																</div>
															</div>
														</li>
													{/each}
												</div>
											</div>
										</div>
									</div>
									<div class="simplebar-placeholder" style="width: 0px; height: 0px;" />
								</div>
								<div class="simplebar-track simplebar-horizontal" style="visibility: hidden;">
									<div class="simplebar-scrollbar" style="width: 0px; display: none;" />
								</div>
								<div class="simplebar-track simplebar-vertical" style="visibility: hidden;">
									<div
										class="simplebar-scrollbar"
										style="height: 0px; transform: translate3d(0px, 0px, 0px); display: none;"
									/>
								</div>
							</ul>
							<div class="border-top px-3 pt-3 pb-0">
								<a href="/notificacion" class="text-link fw-semi-bold">
									Ver todas las notificaciones
								</a>
							</div>
						</div>
					</div>
				</li>
			{/if}
			{#if total_periodos > 0}
				<li class="dropdown stopevent">
					<a
						class="btn btn-link d-none d-md-block d-lg-block"
						href="#{periodo ? periodo.id : 0}"
						id="dropdownPeriodos"
						style="font-size: 12px !important; text-decoration: none;"
					>
						{periodo ? periodo.nombre_completo : 0}
					</a>
					<a
						class="btn btn-light btn-icon rounded-circle text-muted d-md-none d-lg-none"
						href="#{periodo ? periodo.id : 0}"
						role="button"
						id="dropdownPeriodos"
						data-bs-toggle="dropdown"
						aria-haspopup="true"
						aria-expanded="false"
					>
						<i class="fe fe-filter" />
					</a>
					<div
						class="dropdown-menu dropdown-menu-end dropdown-menu-lg"
						aria-labelledby="dropdownPeriodos"
					>
						<div class=" ">
							<div
								class="border-bottom px-3 pb-3 d-flex justify-content-between align-items-center"
							>
								<span class="h4 mb-0">Periodos académicos</span>
							</div>
							<div
								class="slimScrollDiv"
								style="position: relative; width: auto; {total_periodos > 5
									? 'height: 360px !important; overflow-x: auto !important;'
									: 'height: auto !important;'}"
							>
								<ul class="list-group list-group-flush notification-list-scroll" style="">
									{#each periodos as ePeriodo, i}
										{#if periodo && periodo.id == ePeriodo.id}
											<li class="list-group-item bg-light">
												<div class="row">
													<div class="col">
														<a class="text-body" href="#{ePeriodo.id}">
															<div class="d-flex">
																<div class="ms-0">
																	<p class="fw-bold mb-1">{ePeriodo.nombre_completo}</p>
																</div>
															</div>
														</a>
													</div>
													<div class="col-auto text-center me-2">
														<a
															href="#{ePeriodo.id}"
															class="badge-dot bg-info"
															data-bs-toggle="tooltip"
															data-bs-placement="top"
															title=""
															data-bs-original-title=""
														/>
													</div>
												</div>
											</li>
										{:else}
											<li class="list-group-item">
												<div class="row">
													<div class="col">
														<a
															class="text-body"
															href="#{ePeriodo.id}"
															on:click|preventDefault={() =>
																changeProfile(
																	'token/change/academic_period',
																	{ periodo_id: ePeriodo.id },
																	1
																)}
														>
															<div class="d-flex">
																<div class="ms-0">
																	<p class="mb-1">{ePeriodo.nombre_completo}</p>
																</div>
															</div>
														</a>
													</div>
													<div class="col-auto text-center me-2">
														<a
															href="#{ePeriodo.id}"
															class="badge-dot bg-secondary"
															data-bs-toggle="tooltip"
															data-bs-placement="top"
															title=""
															data-bs-original-title=""
														/>
													</div>
												</div>
											</li>
										{/if}
									{/each}
								</ul>
							</div>
						</div>
					</div>
				</li>
			{/if}
			{#if isLoadPersona}
				<li class="dropdown ms-2">
					<a
						class="rounded-circle"
						href="#foto"
						role="button"
						id="dropdownUser"
						data-bs-toggle="dropdown"
						aria-expanded="false"
					>
						<div class="avatar avatar-md">
							<img
								alt="avatar"
								src={persona.foto}
								onerror="this.onerror=null;this.src='./image.png'"
								class="rounded-circle"
							/>
						</div>
					</a>
					<div class="dropdown-menu dropdown-menu-end" aria-labelledby="dropdownUser">
						<div class="dropdown-item">
							<div class="d-flex">
								<div class="avatar avatar-md">
									<img
										alt="avatar"
										src={persona.foto}
										onerror="this.onerror=null;this.src='./image.png'"
										class="rounded-circle"
									/>
								</div>
								<div class="ms-3 lh-1">
									<h5 class="mb-1">{persona.nombre_completo}</h5>
									<p class="mb-0 text-muted">{persona.correo_institucional}</p>
								</div>
							</div>
						</div>
						<div class="dropdown-divider" />
						<ul class="list-unstyled">
							{#if perfiles}
								{#each perfiles as perfil}
									<li>
										{#if perfilprincipal.id == perfil.id}
											<a class="dropdown-item active" href="#{perfil.id}">
												<i class="bi bi-check-square-fill me-2" />
												{perfil.carrera}
											</a>
										{:else}
											<a
												class="dropdown-item"
												href="#{perfil.id}"
												on:click|preventDefault={() =>
													changeProfile('token/change/career', { perfil_id: perfil.id }, 2)}
											>
												<i class="bi bi-dash-square me-2" />
												{perfil.carrera}
											</a>
										{/if}
									</li>
								{/each}
							{/if}
						</ul>
						<div class="dropdown-divider" />
						<ul class="list-unstyled">
							<li>
								<a class="dropdown-item" href="/" on:click|preventDefault={gestionarPerfil}>
									<i class="fe fe-user me-2" /> Gestionar mi perfil
								</a>
							</li>
							<li>
								<a class="dropdown-item" href="/changepicture">
									<i class="bi bi-person-bounding-box  me-2" /> Cambiar foto de perfil
								</a>
							</li>
							<li>
								<a class="dropdown-item" href="/" on:click|preventDefault={openModalChangePassword}>
									<i class="fe fe-lock me-2" /> Cambiar contraseña
								</a>
							</li>
						</ul>
						<div class="dropdown-divider" />
						<ul class="list-unstyled">
							<li>
								<a class="dropdown-item" href="javascript:;" on:click|preventDefault={logOutUser}>
									<i class="fe fe-power me-2" /> Cerrar Sesión
								</a>
							</li>
						</ul>
					</div>
				</li>
			{/if}
		</ul>
	</div>
</nav>
<div class="bg-sga-2 navbar-fixed-top" style="height: 11px;" />
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="lg"
		on:actionRun={actionRun}
	/>
{/if}

<style>
	.bg-sga {
		--bs-bg-opacity: 1;
		background-color: #1c3247 !important;
	}
	.bg-sga-2 {
		--bs-bg-opacity: 1;
		background-color: #fe9900 !important;
	}
	.top-20 {
		top: 20% !important;
	}
	#dropdownNotification:hover,
	#dropdownNotification.text-muted:hover,
	#dropdownNotification:hover .text-primary-hover {
		color: #ffc107 !important;
	}
	.indicator-primary.indicator:before {
		background-color: #ffc107;
	}
	.bg-dark {
		background-color: #1c3247 !important;
	}
	.navbar-fixed-top {
		right: 0;
		left: 0;
		z-index: 1030;
		margin-bottom: 0;
		overflow: visible;
	}
	.navbar-brand > img {
		height: 1.875rem;
	}
	.btn-link {
		color: white !important;
	}
	.btn-link:hover {
		color: #d8ac66 !important;
		font-weight: bold;
	}
	.list-unstyled li,
	.list-unstyled li a {
		white-space: normal;
		float: left;
		width: 100%;
		height: auto;
		word-wrap: break-word;
	}
</style>
