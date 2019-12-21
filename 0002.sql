
--
-- Alter field bcid on bookcopy
--
ALTER TABLE "LIBRARY_BOOKCOPY" MODIFY "BCID" DEFAULT 'dd0311d1138040929cda2f900e708bd5';
ALTER TABLE "LIBRARY_BOOKCOPY" MODIFY "BCID" DEFAULT NULL;
--
-- Alter field rid on room
--
--
-- Alter field rname on room
--
--
-- Alter field rpos on room
--
COMMIT;
