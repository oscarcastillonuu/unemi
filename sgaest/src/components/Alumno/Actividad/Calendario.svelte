<script lang="ts">
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { Icon, Tooltip, Popover } from 'sveltestrap';
	import { loading } from '$lib/store/loadingStore';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addNotification } from '$lib/store/notificationStore';
	export let aData;
	let month_display;
	let month;
	let year;
	let eMatricula;
	let aCalendario = [];
	let aTipoActividades = [];
	const dispatch = createEventDispatcher();

	onMount(async () => {
		month_display = aData.month_display;
		eMatricula = aData.eMatricula;
		month = aData.month;
		year = aData.year;
		aCalendario = aData.aCalendario;
		aTipoActividades = aData.aTipoActividades;
	});

	const renderizarCalendario = (calendario) => {
		aCalendario = [];
		calendario.forEach((element) => {
			console.log(element);
			aCalendario.push(element);
		});
	};

	const actionLoadCalendar = async (action, mes, anio) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const id = eMatricula.id;
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/general/data', {
			action: 'detail_calenar_student',
			id: id,
			mover: action,
			mes: month,
			anio: year
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
				console.log(res.data);
				month_display = res.data.month_display;
				eMatricula = res.data.eMatricula;
				month = res.data.month;
				year = res.data.year;
				//renderizarCalendario(res.data.aCalendario);
				aCalendario = res.data.aCalendario;
				aTipoActividades = res.data.aTipoActividades;
			}
		}
	};
</script>

<!--<div class="row">
	<div class="col-md-8 col-12">
		<h5 class="mb-3">{mensaje}</h5>
	</div>
</div>-->
<div class="row">
	<div class="col-lg-3">
		<h4>Actividades</h4>
		{#if aTipoActividades.length > 0}
			<ul class="list-group list-group-flush">
				{#each aTipoActividades as aTipoActividad}
					<li class="list-group-item d-flex justify-content-between align-items-start px-1">
						<div class="ms-2 me-auto">
							<div class="fw-bold">{aTipoActividad[1]}</div>
						</div>
						<span class=""><Icon
							name="square-fill"
							class="fs-6 me-2"
							style="color: {aTipoActividad[2]} !important;"
						/></span>
					</li>
				{/each}
				
			</ul>
			
		{:else}
			<p>Sin actividades en el mes</p>
		{/if}
	</div>
	<div class="col-lg-9">
		<div class="table-responsive">
			<table
				class="table table-sm mb-0 text-nowrap table-border table table-bordered calendar-table table table-condensed table-tight"
				style="white-space: nowrap; width: 100%"
			>
				<thead class="table-light">
					<tr>
						<th scope="col" class="text-center" style="width: 5%; vertical-align: middle;"
							><button
								type="button"
								class="btn btn-light p-0"
								on:click|preventDefault={() => actionLoadCalendar('before', month, year)}
								><Icon name="caret-left-fill" /></button
							></th
						>
						<th
							scope="col"
							class="text-center p-0"
							style="width: 90%; vertical-align: middle;"
							colspan="5">{month_display}</th
						>
						<th scope="col" class="text-center" style="width: 5%; vertical-align: middle;"
							><button
								type="button"
								class="btn btn-light p-0"
								on:click|preventDefault={() => actionLoadCalendar('after', month, year)}
								><Icon name="caret-right-fill" /></button
							></th
						>
					</tr>
					<tr>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Lunes</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Martes</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Miercoles</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Jueves</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Viernes</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Sábado</th
						>
						<th scope="col" class="text-center" style="vertical-align: middle;" width="14.285%"
							>Domingo</th
						>
					</tr>
				</thead>
				<tbody>
					{#each aCalendario as semanas}
						<tr />
						{#each semanas as semana}
							<td
								class="text-center calendar-day "
								style="vertical-align: middle; {semana.actividades.length > 0
									? 'background-color: #f5f5f5 !important;'
									: ''}"
							>
								<div class={!semana.monthActive ? 'date' : ''} style="display: block;">
									{semana.day}
								</div>
								{#if semana.actividades.length > 0}
									{#each semana.actividades as actividad}
										<a class="p-0 m-0" href={actividad.url} target="_blank">
											<i
												style="color: {actividad.background} !important;"
												class="fs-5 m-0 bi-square-fill"
												id={`Popover_${actividad.id}`}
											/>
											<Popover
												trigger="hover"
												target={`Popover_${actividad.id}`}
												placement="top"
												title={`${actividad.tipo_display}`}
												>{actividad.eMateria.display} -> {actividad.eActividad.display}</Popover
											></a
										>
									{/each}
								{/if}
							</td>
						{/each}
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

<style>
	.table td,
	.table th {
		padding: 0.5rem;
		vertical-align: top;
		border-top: 1px solid #dee2e6;
	}

	.date {
		color: #ccc;
	}
	.event.end {
		border-right: 1px solid #b2dba1;
		border-top-right-radius: 4px;
		border-bottom-right-radius: 4px;
	}
	.event.begin {
		border-left: 1px solid #b2dba1;
		border-top-left-radius: 4px;
		border-bottom-left-radius: 4px;
	}
	.event {
		border-top: 1px solid #b2dba1;
		border-bottom: 1px solid #b2dba1;
		background-image: linear-gradient(to bottom, #dff0d8 0px, #c8e5bc 100%);
		background-repeat: repeat-x;
		color: #3c763d;
		border-width: 1px;
		font-size: 0.75em;
		padding: 0 0.5em;
		line-height: 1em;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		margin-bottom: 1px;
	}
	.calendar-day {
		width: 100px;
		min-width: 100px;
		max-width: 100px;
		height: 40px;
	}
	.calendar-table {
		margin: 0 auto;
		width: auto;
	}
	.selected {
		background-color: #eee;
	}
	.outside .date {
		color: #ccc;
	}
	.timetitle {
		white-space: nowrap;
		text-align: right;
	}
	.event {
		border-top: 1px solid #b2dba1;
		border-bottom: 1px solid #b2dba1;
		background-image: linear-gradient(to bottom, #dff0d8 0px, #c8e5bc 100%);
		background-repeat: repeat-x;
		color: #3c763d;
		border-width: 1px;
		font-size: 0.75em;
		padding: 0 0.5em;
		line-height: 1em;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		margin-bottom: 1px;
	}
	.event.begin {
		border-left: 1px solid #b2dba1;
		border-top-left-radius: 4px;
		border-bottom-left-radius: 4px;
	}
	.event.end {
		border-right: 1px solid #b2dba1;
		border-top-right-radius: 4px;
		border-bottom-right-radius: 4px;
	}
	.event.all-day {
		border-top: 1px solid #9acfea;
		border-bottom: 1px solid #9acfea;
		background-image: linear-gradient(to bottom, #d9edf7 0px, #b9def0 100%);
		background-repeat: repeat-x;
		color: #31708f;
		border-width: 1px;
	}
	.event.all-day.begin {
		border-left: 1px solid #9acfea;
		border-top-left-radius: 4px;
		border-bottom-left-radius: 4px;
	}
	.event.all-day.end {
		border-right: 1px solid #9acfea;
		border-top-right-radius: 4px;
		border-bottom-right-radius: 4px;
	}
	.event.clear {
		background: none;
		border: 1px solid transparent;
	}
	.table-tight > thead > tr > th,
	.table-tight > tbody > tr > th,
	.table-tight > tfoot > tr > th,
	.table-tight > thead > tr > td,
	.table-tight > tbody > tr > td,
	.table-tight > tfoot > tr > td {
		padding-left: 0;
		padding-right: 0;
	}
	.table-tight-vert > thead > tr > th,
	.table-tight-vert > tbody > tr > th,
	.table-tight-vert > tfoot > tr > th,
	.table-tight-vert > thead > tr > td,
	.table-tight-vert > tbody > tr > td,
	.table-tight-vert > tfoot > tr > td {
		padding-top: 0;
		padding-bottom: 0;
	}
</style>
