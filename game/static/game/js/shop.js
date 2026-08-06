(() => {
    const storageKey = (
        `game-rpg-shop-state:${window.location.pathname}`
    );

    function getShopCategories() {
        return Array.from(
            document.querySelectorAll(".shop-category")
        );
    }

    function saveShopState() {
        const categories = getShopCategories();

        const openCategories = categories
            .map((category, index) => {
                return category.open ? index : null;
            })
            .filter((index) => index !== null);

        const shopState = {
            scrollY: window.scrollY,
            openCategories: openCategories,
        };

        sessionStorage.setItem(
            storageKey,
            JSON.stringify(shopState),
        );
    }

    function restoreShopState() {
        const savedState = sessionStorage.getItem(storageKey);

        if (!savedState) {
            return;
        }

        sessionStorage.removeItem(storageKey);

        try {
            const shopState = JSON.parse(savedState);
            const categories = getShopCategories();

            const openCategories = Array.isArray(
                shopState.openCategories,
            )
                ? shopState.openCategories
                : [];

            categories.forEach((category, index) => {
                category.open = openCategories.includes(index);
            });

            const scrollY = Number.isFinite(shopState.scrollY)
                ? shopState.scrollY
                : 0;

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    window.scrollTo({
                        top: scrollY,
                        left: 0,
                        behavior: "auto",
                    });
                });
            });
        } catch {
            sessionStorage.removeItem(storageKey);
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        const shopForms = document.querySelectorAll(
            ".shop-layout form",
        );

        shopForms.forEach((form) => {
            form.addEventListener(
                "submit",
                saveShopState,
            );
        });

        restoreShopState();
    });
})();