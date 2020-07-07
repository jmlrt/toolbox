# Backup management

FILES :=
FORCE := false

.PHONY: encrypt
encrypt:
	for FILE in $(FILES); do \
		gpg --cipher-algo AES256 --compress-algo zlib  --output $$FILE.gpg --symmetric $$FILE; \
	done

.PHONY: decrypt
decrypt:
	for FILE in $(basename $(FILES)); do \
		gpg --output $$FILE --decrypt $$FILE.gpg; \
	done

.PHONY: test
test:
	for FILE in $(basename $(FILES)); do \
		gpg --output $$FILE.bak --decrypt $$FILE.gpg; \
		sha256sum $$FILE $$FILE.bak; \
	done

.PHONY: checksum
checksum:
	for FILE in $(FILES); do \
		sha256sum $$FILE > $$FILE.sha256; \
	done

.PHONY: shred
shred:
ifeq ($(FORCE),true)
	for FILE in $(FILES); do \
		shred -u $$FILE; \
		shred -u $$FILE.bak; \
	done
else
	echo "This will shred the following files:"; \
	for FILE in $(FILES); do \
		echo $$FILE $$FILE.bak; \
	done
endif