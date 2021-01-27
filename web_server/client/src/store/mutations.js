class GenericMutations {
    getCrud () {
        return ({
            ADD_ITEM: (state, newItem) => state.items.push(newItem),
            ADD_ITEMS: (state, newItems) => state.items = state.items.concat(newItems).filter(
                (item, index, self) => {
                    const _item = JSON.stringify(item);
                    return index === self.findIndex(obj => JSON.stringify(obj) === _item);
                }
            )
        });
    }
}

export default GenericMutations;
