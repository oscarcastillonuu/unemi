<script lang="ts">
	import Svelecte, { config } from 'svelecte';
	import { createEventDispatcher, onMount } from 'svelte';
	/*import {
		dndzone,
		overrideItemIdKeyNameBeforeInitialisingDndZones,
		setDebugMode
	} from 'svelte-dnd-action';*/
	export let options = [];
	export let inputId = undefined;
	export let name = undefined;
	export let valueField = 'id';
	export let labelField = 'name';
	export let labelAsValue = false;
	export let resetOnBlur = true;
	export let fetchResetOnBlur = true;
	export let multiple = false;
	export let minQuery = 2;
	export let value;
	export let placeholder = '';
	export let fetch = null;
	export let required = false;
	export let disabled = false;
	export let valueAsObject = true;
	export let clearable = true;
	export let parent = null;
	export let selectOnTab = true;
	export let readSelection = null;
	// let payload = null;
	// overrideItemIdKeyNameBeforeInitialisingDndZones(labelField);
	// setDebugMode(true);
	// config.i18n defaults:
	const dispatch = createEventDispatcher();
	config.i18n = {
		empty: 'Sin opciones',
		nomatch: 'Sin opciones de coincidencia',
		max: (num) => `Elementos máximos ${num} seleccionados`,
		fetchBefore: 'Escribe para empezar a buscar',
		fetchQuery: (minQuery, inputLength) =>
			`Escriba ${
				minQuery > 1 && minQuery > inputLength
					? `por lo menos ${minQuery - inputLength} caracteres `
					: ''
			}para empezar a buscar`,
		fetchEmpty: 'No hay datos relacionados con su búsqueda',
		collapsedSelection: (count) => `${count} seleccionado`,
		createRowLabel: (value) => `Crear '${value}'`
	};

	/**
	 * NOTE: We do not define initial value for `options` property. Initial options are created from `value` property.
	 * To make this conversion automatic, `valueAsObject` must be set to `true`
	 */
	onMount(async () => {
		// console.log(`value: ${value}`);
		if (inputId === undefined) {
			const randon = Math.floor(Math.random() * 100);
			inputId = `id_select_search_${randon}`;
		}
		if (name === undefined) {
			const randon = Math.floor(Math.random() * 100);
			name = `name_select_search_${randon}`;
		}
	});

	function changeSelect(event) {
		//value = null;
		//console.log(event);
		dispatch('actionChangeSelectSearch', { ...event.detail });
	}
</script>

<Svelecte
	{options}
	{selectOnTab}
	{disabled}
	{required}
	{valueField}
	{name}
	{labelField}
	{resetOnBlur}
	{fetchResetOnBlur}
	{valueAsObject}
	{labelAsValue}
	{minQuery}
	{multiple}
	bind:value
	bind:readSelection
	{placeholder}
	{fetch}
	{clearable}
	{parent}
	on:change={changeSelect}
/>
