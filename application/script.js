document.addEventListener('gesturestart', function (e) {
      e.preventDefault();
        copyCode(getSelectedCode());
        });

        document.addEventListener('touchmove', function (e) {
          e.preventDefault();
            copyCode(getSelectedCode());
            });

            document.addEventListener('keydown', function (e) {
              if (e.ctrlKey && (e.key === '+' || e.key === '-')) {
                  e.preventDefault();
                      copyCode(getSelectedCode());
                        }
                        });
})