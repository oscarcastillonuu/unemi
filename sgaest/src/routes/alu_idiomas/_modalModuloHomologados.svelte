<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { variables } from '$lib/utils/constants';
	import {Alert} from "sveltestrap";
	export let aData;

	onMount(async () => {});
	let eGrupoInscripcion = aData.eGrupoInscripcion;
</script>
<div class="row">
	<Alert color="info"><span class="fw-bold">Calificación obtenida: {eGrupoInscripcion.nota} pts.</span></Alert>
</div>
<div class="row mb-5">
     <table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
		<thead class="table-ligth">
		<tr>
			<td colspan="4"><h4 class="">Tabla de homologación de módulo de acuerdo al puntaje obtenido.</h4></td>
		</tr>
			<tr>
				<th scope="col" class="border-top-0 text-center align-middle ">Rango de calificación</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Módulos aprobados</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Módulo a continuar</th>
			</tr>
		</thead>
		<tbody>
           <tr scope="col" class="border-top-0 text-center align-middle ">
            <td>70</td>
            <td>INGLES I (GENERAL ENGLISH)</td>
            <td>{#if eGrupoInscripcion.nota === 70}<span class="badge bg-success">INGLES II (GENERAL ENGLISH)</span>{/if}</td>
        </tr>
        <tr scope="col" class="border-top-0 text-center align-middle ">
            <td>70 - 80</td>
            <td>INGLES I (GENERAL ENGLISH) <br> INGLES II (GENERAL ENGLISH)</td>
            <td>{#if eGrupoInscripcion.nota >70 && eGrupoInscripcion.nota <= 80}<span class="badge bg-success">INGLES III (GENERAL ENGLISH)</span>{/if}</td>
        </tr>
        <tr scope="col" class="border-top-0 text-center align-middle ">
            <td> 80 - 90</td>
            <td>INGLES I (GENERAL ENGLISH) <br>  INGLES II (GENERAL ENGLISH) <br>  INGLES III (GENERAL ENGLISH) </td>
			<td>{#if eGrupoInscripcion.nota >80 && eGrupoInscripcion.nota <= 90}<span class="badge bg-success">INGLES IV (GENERAL ENGLISH)</span>{/if}</td>
        </tr>

         <tr scope="col" class="border-top-0 text-center align-middle ">
            <td>90 - 100</td>
            <td>INGLES I (GENERAL ENGLISH) <br>  INGLES II (GENERAL ENGLISH) <br> INGLES III (GENERAL ENGLISH) <br>  INGLES IV (GENERAL ENGLISH)</td>
			 <td>{#if eGrupoInscripcion.nota > 90 && eGrupoInscripcion.nota <= 100}<span class="badge bg-success">INGLES V (GENERAL ENGLISH)</span>{/if}</td>
        </tr>


        </tbody>
	</table>
</div>

<div class="row">
<!--	<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">-->
<!--		<thead class="table-ligth">-->
<!--		<tr>-->
<!--			<td colspan="4"><h4 class="">Módulos aprobados</h4></td>-->
<!--		</tr>-->
<!--			<tr>-->
<!--				<th scope="col" class="border-top-0 text-center align-middle ">N°</th>-->
<!--				<th scope="col" class="border-top-0 text-center align-middle ">Módulos aprobados</th>-->
<!--			</tr>-->
<!--		</thead>-->
<!--		<tbody>-->
<!--		{#each eGrupoInscripcion.obtener_asignaturas_homologadas as modulo, index}-->
<!--			<tr scope="col" class="border-top-0 text-center align-middle ">-->
<!--				<td>-->
<!--					{index+1}-->
<!--				</td>-->
<!--				<td scope="col" class="border-top-0 text-center align-middle ">-->
<!--					<span class="badge bg-success">{modulo.display}</span>-->
<!--				</td>-->
<!--			</tr>-->
<!--		{/each}-->

<!--		</tbody>-->
<!--	</table>-->
</div>