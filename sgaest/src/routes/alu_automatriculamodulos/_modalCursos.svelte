<script lang="ts">
	import {loading} from "$lib/store/loadingStore";

	export let aData;
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { onMount } from 'svelte';
	import {apiGET, apiPOST} from "$lib/utils/requestUtils";
	import Swal from "sweetalert2";
	import {addToast} from "$lib/store/toastStore";
	let cursos = aData.data.cursos;
	let materiasArray;
	
	let materiasseleccionadas = [];
	let materiasseleccionadas_key = 0;
	const dispatch = createEventDispatcher();
	function actionRun(event) {
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

	const actionSeleccionarMateria = async (materia,display) => {
		const mensaje = {
			title: 'CONFIRMACIÓN DE INSCRIPCIÓN',
			html: '¿ESTÁ SEGURO DE MATRICULARSE EN LA MATERIA: <b>'+display+ '</b>?',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Confirmar`,
			cancelButtonText: 'Cancelar'
		};
		if (materiasseleccionadas.length > 0) {
			materiasseleccionadas.splice(0, materiasseleccionadas.length);
			//remover_btn_remover(materia.id)
		} else {
			Swal.fire(mensaje)
			.then(async (result)=>{
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/alu_automatriculamodulos	', {
						action: 'seeleccionarMateria',
						id:materia.id,
					});
					loading.setLoading(false, 'Cargando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'warning', header: 'Advertencia', body: errors[0].error });
						dispatch('actionRun', {action: 'nextProccess', value: 1});//closeModalReload
						return;
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'warning', header: 'Advertencia', body: res.message });
							dispatch('actionRun', {action: 'nextProccess', value: 1});//closeModalReload
							return;
						} else {
							let datos_ = {
								value: 1,
								asignatura:cursos[0],
								materia:materia
							}
							//remover_btn_seleccionar(materia.id)
							materiasseleccionadas.push(materia);
							materiasseleccionadas_key++; //mando a actualizar los datos
							actionMatricular();
						}
					}
				}
			}).catch((error) => {
				addToast({ type: 'warning', header: 'Advertencia', body: error });
				return;
			});
		}
	}
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
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/alu_automatriculamodulos	', {
				action: 'matricular',
				tiene_matricula: aData.tiene_matricula,
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
	}
	onMount(async () => {});
	console.log(aData)
	materiasArray = Object.entries(cursos[0].materias).map(([nombre, materia]) => ({ nombre, ...materia }));
	materiasArray.sort((a, b) => a.cupo - a.matriculados - (b.cupo - b.matriculados));
	let materiaSeleccionada = materiasArray[0];

</script>
<div class="row">
    <h3>{cursos[0].asignatura}</h3><br>
	
</div>
<div class="row">
	<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
		<thead class="table-ligth">
			<tr>
				<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Paralelo</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Inicio/Fin</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Disp.</th>
				<th scope="col" class="border-top-0 text-center align-middle " />
			</tr>
		</thead>
		<tbody>
        {#each materiasArray as materia, index}
			{#if materia === materiaSeleccionada}
			<tr scope="col" class="border-top-0 text-center align-middle ">
                <td> {index+1}</td>
                <td> {materia.paralelo}</td>
                <td> <b>Inicio: </b>{materia.inicio} <br> <b>Fin: </b>{materia.fin}</td>
                <td> {materia.cupo - materia.matriculados}</td>
				<td>
					<button on:click|preventDefault={() => actionSeleccionarMateria(materia,cursos[0].asignatura + ", PARALELO: " + materia.paralelo)}
						class="btn btn-xs btn-success rounded-pill text-white" id={materia.id} type="button" > Matricular
					</button>
				</td>
			</tr>
			{/if}
        {/each}

		</tbody>
	</table>
</div>
