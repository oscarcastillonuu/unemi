<script lang="ts">
	import {createEventDispatcher, onMount} from 'svelte';
	import { Spinner } from 'sveltestrap';
	import {loading} from "$lib/store/loadingStore";
	import {apiGET, apiPOST} from "$lib/utils/requestUtils";
	import {addNotification} from "$lib/store/notificationStore";
	import ModalCurso from ".//_modalCursos.svelte";
	import ModalGenerico from '../../components/Alumno/Modal.svelte';
	import Swal from "sweetalert2";
	import {addToast} from "$lib/store/toastStore";
	export let data;

    let load = true;
	let aDataModal = {};
	let aplacement = '';
	let modalDetalleOffCanvasContent;
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenOffCanvasGenerico = false;
	let modalTitle = '';
	let materiasseleccionadas = [];
	let asignatura  = [];
	let materiasseleccionadas_key = 0;
    onMount(async () => {
        if (data !== undefined) {
            load = false;
        }
    });
	const dispatch = createEventDispatcher();

	function actionRun(event) {
        mOpenModalGenerico = false;
		dispatch('actionRun', event.detail);
	}

	function remover_btn_seleccionar(id){
		const button = document.getElementById(id);
		button.innerText = 'Remover';
		button.classList.remove('btn-success');
		button.classList.add('btn-danger');
	}

	function remover_btn_remover(id){
		const button = document.getElementById(id);
		button.innerText = 'Seleccionar';
		button.classList.remove('btn-danger');
		button.classList.add('btn-success');
		materiasseleccionadas_key++;
	}

	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	const loadCursos = async (id,pk=0) => {
		if (materiasseleccionadas.length > 0) {
			materiasseleccionadas.splice(0, materiasseleccionadas.length);
			remover_btn_remover(pk)
		} else {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/alu_automatriculamodulos', {
				action: 'loadCursos',
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
					aDataModal = {data:res.data,tiene_matricula:data.tiene_matricula};
					modalDetalleContent = ModalCurso;
					mOpenModalGenerico = !mOpenModalGenerico;
					modalTitle = 'CURSOS DISPONIBLES';
				}
			}
		}
    };

	const actionMatricular = async () => {
		if (materiasseleccionadas.length === 0) {
			Swal.fire(
					{
						icon: 'error',
						title: 'ATENCIÓN',
						html: "Debe seleccionar al menos 1 materia",
						type: 'warning'
					}
			)
		} else {
			let idsMaterias = [];
			materiasseleccionadas.forEach((materia) => {
				idsMaterias.push(materia.id);
			});
			const mensaje = {
				title: 'CONFIRMACIÓN DE MATRICULA',
				html: '¿Al confirmar, usted se estar&iacute;a matriculando en '+materiasseleccionadas.length+', materia(s)?',
				icon: 'warning',
				showCancelButton: true,
				allowOutsideClick: false,
				confirmButtonColor: '#3085d6',
				cancelButtonColor: '#d33',
				confirmButtonText: `Confirmar`,
				cancelButtonText: 'Cancelar'
			};
			Swal.fire(mensaje)
					.then(async (result) => {
						if (result.value) {
							loading.setLoading(true, 'Cargando, espere por favor...');
							const [res, errors] = await apiPOST(fetch, 'alumno/alu_automatriculamodulos	', {
								action: 'matricular',
								tiene_matricula: data.tiene_matricula,
								idsMaterias: idsMaterias,
							}
							);
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (errors.length > 0) {
								addToast({type: 'warning', header: 'Advertencia', body: errors[0].error});
								return;
							} else {
								if (!res.isSuccess) {
									addToast({type: 'warning', header: 'Advertencia', body: res.message});
									return;
								} else {
									addToast({type: 'info', header: 'Información', body: res.data['mensaje']});
									dispatch('actionRun', {action: 'nextProccess', value: 1});//closeModalReload
								}
							}
						}
					}).catch((error) => {
				addToast({type: 'warning', header: 'Advertencia', body: error});
				return;
			});
		}
	}
</script>
{#if !load}
	<div class="row align-items-center">
		<div class="col-xl-12 col-lg-12 col-md-12 col-12">
			<div class="d-flex col align-items-end justify-content-between bg-white px-4 pt-4 pb-4 rounded-none rounded-bottom-md shadow-sm">
				<div class="d-flex col align-items-center">
					<div class="me-4 position-relative d-flex justify-content-end align-items-end mt-n5 d-none d-sm-block d-sm-none d-md-block">
						<img src={data.inscripcion.persona.foto_perfil}
							 onerror="this.onerror=null;this.src='./image.png'"
							 class="avatar-xxl rounded-circle border border-4 border-white"/>
						<a href="#" class="position-absolute mt-2 ms-n3" data-bs-toggle="tooltip" data-placement="top"
						   title="Verifed">
							<img src="./assets/images/svg/checked-mark.svg" alt="" height="35" width="35"/>
						</a>
					</div>
					<div class="lh-1">
						<h2 class="mb-2">{data.inscripcion.display}</h2>
						<b>Malla:</b> {data.malla.display}<br>
						<b>Carrera:</b> {data.inscripcion.carrera.display}<br>
						<b>Nivel:</b> {data.nivel.display} <br>
						{#if data.tiene_matricula===false}<span class="mt-3 badge bg-warning">Grupo Socio Económico: {data.fichasocioeconomicainec }</span>{/if}
					</div>


				</div>

				<!--<div class="text-end">
					<button on:click|preventDefault={() => actionMatricular()} class="btn btn-primary btn-lg"
							type="button">Matricular
					</button>
				</div>-->
			</div>
		</div>
	</div>
	<div class="row mt-3">
		{#key materiasseleccionadas_key}

				<div class="col-lg-12 col-md-12 col-12">
					<div class="card">
						<div class="card-header">
							<h4 class="mb-1"> Materias seleccionadas: {materiasseleccionadas.length}</h4>
						</div>
						{#if materiasseleccionadas.length > 0}
							<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
								<thead class="table-ligth">
								<tr>
									<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
									<th scope="col" class="border-top-0 text-center align-middle ">Asingatura</th>
									<th scope="col" class="border-top-0 text-center align-middle ">Paralelo</th>
									<th scope="col" class="border-top-0 text-center align-middle ">Inicio - Fin</th>
								</tr>
								</thead>
								<tbody>
								{#each materiasseleccionadas as materia, index}
									<tr scope="col"
										class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
										<td>{index + 1}</td>
										<td> {asignatura.asignatura}</td>
										<td> {materia.paralelo}</td>
										<td><b>Inicio: </b>{materia.inicio} <br> <b>Fin: </b>{materia.fin}</td>
									</tr>
								{/each}
								</tbody>
							</table>
						{/if}
					</div>
				</div>
		{/key}
	</div>
	<div class="row mt-5">
		<div class="col-lg-12 col-md-12 col-12">
			<div class="card">
				<div class="card-header">
					<h4 class="mb-1">Módulos</h4>
				</div>
				<!-- Table -->
				<div
					class="table table-striped text-nowrap mb-0 table-responsive border-0 overflow-y-hidden table-sm"
				>
					<table class="table mb-0 text-nowrap">
						<thead class="table-light">
							<tr>
								<th class="border-0 text-center" scope="row">#</th>
								<th class="border-0 text-center">Asignatura</th>
								<th class="border-0 text-center">Disponible</th>
								<th class="border-0 text-center">Estado</th>
							</tr>
						</thead>
						<tbody>
                        {#each data.eAsignatura as datos, index}
                          <tr scope="col" class="border-top-0 text-center align-middle ">
                              <td class="align-middle border-top-0">
                                  {index+1}
                              </td>
                              <td class="align-middle border-top-0">
                                  {datos.asignatura.display}
                              </td>
                              <td class="align-middle border-top-0">
									{#if datos.puede_tomar_materia === true}
										{#if datos.estado_asignatura !==1}
											 <button on:click|preventDefault={() => loadCursos(datos.asignatura.id,datos.asignatura.pk)} id = {datos.asignatura.pk} class="btn btn-success  btn-sm  rounded-pill text-white" type="button"> Seleccionar </button>
										{/if}
									{/if}
                              </td>
							   <td class="align-middle border-top-0">
								   {#if datos.estado_asignatura ===1}<span class="badge bg-success">APROBADA</span>{:else if datos.estado_asignatura ===2} <span class="badge bg-important">REPROBADO</span> {:else} <span class="badge bg-warning">PENDIENTE</span>{/if}
                              </td>
                          </tr>
                        {/each}
						</tbody>
					</table>
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
