<script>
	import { onMount } from 'svelte';
	import Select from 'svelte-select/Select.svelte';

	export let id = undefined;
	export let name = undefined;
	export let items = [];
	export let clases = `foo bar`;
	export let inputAttributes = { autocomplete: 'off' };
	export let justValue = {};
	export let listAutoWidth = true;
	export let placeholder = '';
	export let searchable = true;
	export let showChevron = true;
	export let itemId = 'value';
	export let loading = false;
	export let label = 'label';
	export let value = null;
	onMount(async () => {
		// console.log(`value: ${value}`);
		if (id === undefined) {
			const randon = Math.floor(Math.random() * 100);
			id = `id_select_${randon}`;
		}
		if (name === undefined) {
			const randon = Math.floor(Math.random() * 100);
			name = `name_select_${randon}`;
		}
	});
</script>

<Select
	{id}
	{name}
	{items}
	{itemId}
	{label}
	{value}
	{placeholder}
	{searchable}
	class={clases}
	{inputAttributes}
	{listAutoWidth}
	{showChevron}
	bind:justValue
	bind:loading
/>

<style>
	:global(.foo) {
		background: pink !important;
	}
	:global(.svelte-select-list, .selected-item) {
		font-family: inherit;
		font-size: 0.765625rem !important;
		color: #18113c;
		font-weight: 400;
		line-height: 1.6;
	}
</style>
