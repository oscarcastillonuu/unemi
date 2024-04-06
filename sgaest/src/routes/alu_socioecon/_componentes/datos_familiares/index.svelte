<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentFormulario from './form.svelte';
	import Swal from 'sweetalert2';
	import { loading } from '$lib/store/loadingStore';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { navigating } from '$app/stores';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let ePersonaDatosFamiliares = [];
	let ePersona = {};
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePersonaDatosFamiliares = aData.ePersonaDatosFamiliares ?? [];
			ePersona = aData.ePersona ?? {};
		}
	});

	const dispatch = createEventDispatcher();
	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosFamiliar') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_2');
			menu.click();
		}
	};

	const eliminarRegistro = (ePersonaDatosFamiliar) => {
		const mensaje = {
			title: `<p style='color:#FE9900;'><b>Acción irreversible</b></p>`,
			html: `<p style='color:#ACAEAF;'>¿Desea eliminar familiar ${ePersonaDatosFamiliar.nombre}</p>`,
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
		Swal.fire({ ...mensaje }).then(async (result) => {
			if (result.value) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
					action: 'deleteDatosFamiliar',
					id: ePersonaDatosFamiliar.pk
				});
				if (errors.length > 0) {
					errors.forEach((element) => {
						addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
					});
				} else {
					if (!res.isSuccess) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					} else {
						addToast({
							type: 'success',
							header: '¡Exitoso!',
							body: res.message
						});
						const menu = document.getElementById('menu_element_2');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};

	const openModalForm = (ePersonaDatosFamiliar) => {
		modalDetalleContent = ComponentFormulario;
		mOpenModal = !mOpenModal;
		// modalTitle = 'Actualizar datos personales';
		aDataModal = { ePersonaDatosFamiliar: ePersonaDatosFamiliar, ePersona: ePersona };
	};
</script>

<div class="card border-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Datos familiares</h3>
			<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
		</div>
		<div>
			<button class="btn btn-success btn-sm" on:click={() => openModalForm(undefined)}
				>Adicionar</button
			>
		</div>
	</div>
	<div class="card-body">
		<div class="table-responsive overflow-y-hidden">
			<table class="table mb-0 text-nowrap table-hover table-centered">
				<thead>
					<tr>
						<th scope="col" class="text-center" style="vertical-align: middle;">Identificación</th>
						<th scope="col" class="text-center" style="vertical-align: middle;"
							>Nombres/Apellidos</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;">Convive</th>
						<th scope="col" class="text-center" style="vertical-align: middle;" />
					</tr>
				</thead>
				<tbody>
					{#if ePersonaDatosFamiliares.length > 0}
						{#each ePersonaDatosFamiliares as ePersonaDatosFamiliar}
							<tr>
								<td class="text-center" style="vertical-align: middle;"
									>{ePersonaDatosFamiliar.identificacion}</td
								>
								<td class="" style="vertical-align: middle;">
									<span class="badge bg-secondary">{ePersonaDatosFamiliar.parentesco.nombre} </span>
									- {ePersonaDatosFamiliar.nombre}

									{#if ePersonaDatosFamiliar.nacimiento}
										<br />
										<span class=""><b>Fecha nacimiento:</b> {ePersonaDatosFamiliar.nacimiento}</span
										>
									{/if}
									{#if ePersonaDatosFamiliar.telefono}
										<br />
										<span class=""><b>Telefono móvil:</b> {ePersonaDatosFamiliar.telefono}</span>
									{/if}
									{#if ePersonaDatosFamiliar.telefono_conv}
										<br />
										<span class=""
											><b>Telefono convencional:</b> {ePersonaDatosFamiliar.telefono_conv}</span
										>
									{/if}
								</td>
								<td class="text-center" style="vertical-align: middle;">
									{#if ePersonaDatosFamiliar.convive}
										<span class="badge bg-success">SI</span>
									{:else}
										<span class="badge bg-danger">NO</span>
									{/if}
								</td>
								<td class="text-center" style="vertical-align: middle;">
									<div class="dropdown dropstart">
										<a
											class="btn-icon btn btn-ghost btn-sm rounded-circle"
											href="#"
											role="button"
											id="Dropdown1"
											data-bs-toggle="dropdown"
											aria-haspopup="true"
											aria-expanded="false"
										>
											<i class="fe fe-more-vertical" />
										</a>
										<div class="dropdown-menu" aria-labelledby="Dropdown1" style="">
											<a
												class="dropdown-item"
												href="#editar"
												on:click={() => openModalForm(ePersonaDatosFamiliar)}
											>
												<i class="fe fe-edit dropdown-item-icon" />Editar
											</a>

											<a
												class="dropdown-item"
												href="#eliminar"
												on:click={() => eliminarRegistro(ePersonaDatosFamiliar)}
											>
												<i class="fe fe-trash dropdown-item-icon" />Eliminar
											</a>
										</div>
									</div>
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
{/if}
