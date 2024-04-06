<script>
	export let item = undefined;
	export const getOptionLabel = undefined;

</script>

<style>
  .customItem {
    display: flex;
    align-items: center;
  }

  .customItem_title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }



  .customItem_tagline {
    display: inline-block;
  }
</style>

<div class="customItem">
  <div class="customItem_title">
    <div class="customItem_tagline">{item.display}</div>
  </div>
</div>
